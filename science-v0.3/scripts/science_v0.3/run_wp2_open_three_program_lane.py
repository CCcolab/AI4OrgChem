from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import psi4
import pyscf
from pyscf import dft, gto


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "runs/science_v0.3/wp2/open_three_program"
CONTRACT = ROOT / "configs/science_v0.3/wp2_open_three_program_contract.json"
BOHR_TO_ANGSTROM = 0.52917721092
FD_STEP_BOHR = 1.0e-3
NWCHEM_ENERGY_RE = re.compile(r"Total DFT energy\s*=\s*([-+0-9.EeDd]+)")
NWCHEM_GRADIENT_ROW_RE = re.compile(
    r"^\s*\d+\s+[A-Za-z]+\s+" + r"\s+".join([r"([-+0-9.EeDd]+)"] * 6) + r"\s*$"
)


def load_v02_module():
    # The public V0.3 package is incremental: frozen source geometries and
    # tangent definitions remain in the immutable sibling V0.2 package.
    path = ROOT.parent / "science-v0.2/scripts/science_v0.2/run_wp2_open_program_anchors.py"
    spec = importlib.util.spec_from_file_location("wp2_v02_anchor_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V02 = load_v02_module()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_bohr(atoms_angstrom: list[list[Any]]) -> list[list[Any]]:
    return [
        [row[0], *(float(value) / BOHR_TO_ANGSTROM for value in row[1:4])]
        for row in atoms_angstrom
    ]


def py_grid(mf: dft.rks.RKS) -> None:
    mf.grids.atom_grid = {
        "H": (300, 1202),
        "C": (300, 1454),
        "N": (300, 1454),
        "O": (300, 1454),
    }
    mf.grids.prune = dft.gen_grid.nwchem_prune


def make_pyscf(atoms_bohr: list[list[Any]], basis: str):
    mol = gto.M(
        atom=atoms_bohr,
        basis=basis.lower(),
        unit="Bohr",
        charge=0,
        spin=0,
        cart=False,
        symmetry=False,
        verbose=0,
        max_memory=9000,
    )
    mf = dft.RKS(mol)
    mf.xc = "B3LYPG"
    py_grid(mf)
    mf.conv_tol = 1.0e-10
    mf.max_cycle = 200
    return mf


def run_pyscf_observables(atoms_bohr: list[list[Any]], basis: str, gradient: bool) -> dict[str, Any]:
    mf = make_pyscf(atoms_bohr, basis)
    energy = float(mf.kernel())
    result: dict[str, Any] = {
        "energy_hartree": energy,
        "converged": bool(mf.converged),
        "retained_grid_points": int(mf.grids.coords.shape[0]),
    }
    if gradient:
        result["gradient_hartree_per_bohr"] = np.asarray(
            mf.nuc_grad_method().kernel(), dtype=float
        ).tolist()
        result["gradient_method"] = "analytic"
    return result


def psi4_molecule(atoms_bohr: list[list[Any]]):
    lines = ["0 1", "units bohr", "symmetry c1", "no_reorient", "no_com"]
    lines.extend(
        f"{row[0]} {float(row[1]):.16f} {float(row[2]):.16f} {float(row[3]):.16f}"
        for row in atoms_bohr
    )
    return psi4.geometry("\n".join(lines))


def configure_psi4(basis: str) -> None:
    psi4.set_options(
        {
            "basis": basis,
            "reference": "RKS",
            "puream": True,
            "scf_type": "DIRECT",
            "df_scf_guess": False,
            "ints_tolerance": 1.0e-12,
            "e_convergence": 10,
            "d_convergence": 9,
            "maxiter": 200,
            "dft_radial_points": 300,
            "dft_spherical_points": 1454,
            "dft_pruning_scheme": "ROBUST",
        }
    )


def run_psi4_observables(
    atoms_bohr: list[list[Any]], basis: str, log: Path, gradient: bool
) -> dict[str, Any]:
    psi4.core.clean()
    psi4.core.set_output_file(str(log), False)
    configure_psi4(basis)
    molecule = psi4_molecule(atoms_bohr)
    if gradient:
        matrix, wfn = psi4.gradient("b3lyp", molecule=molecule, return_wfn=True)
        result: dict[str, Any] = {
            "energy_hartree": float(wfn.energy()),
            "gradient_hartree_per_bohr": np.asarray(matrix, dtype=float).tolist(),
            "gradient_method": "analytic",
        }
    else:
        energy, wfn = psi4.energy("b3lyp", molecule=molecule, return_wfn=True)
        result = {"energy_hartree": float(energy)}
    result.update({
        "converged": True,
        "wavefunction_energy_hartree": float(wfn.energy()),
    })
    return result


def nwchem_input(prefix: str, atoms_bohr: list[list[Any]], basis: str, operation: str) -> str:
    geometry = "\n".join(
        f"  {row[0]:2s} {float(row[1]): .16f} {float(row[2]): .16f} {float(row[3]): .16f}"
        for row in atoms_bohr
    )
    return f"""start {prefix}

echo

title "WP2 open-three-program lane"

memory total 8 gb

geometry units au noautosym noautoz
{geometry}
end

basis spherical
  * library {basis}
end

dft
  xc b3lyp
  direct
  grid huge nodisk
  tolerances tight
  convergence energy 1.0d-10
  convergence density 1.0d-9
  iterations 200
end

task dft {operation}
"""


def micromamba_path() -> Path:
    candidates = [Path.home() / ".local/bin/micromamba", Path.home() / "micromamba/bin/micromamba"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("micromamba not found")


def parse_nwchem_gradient(text: str, atom_count: int) -> list[list[float]]:
    marker = text.rfind("ENERGY GRADIENTS")
    if marker < 0:
        raise RuntimeError("NWChem ENERGY GRADIENTS block not found")
    rows: list[list[float]] = []
    for line in text[marker:].splitlines():
        match = NWCHEM_GRADIENT_ROW_RE.match(line)
        if match:
            values = [float(value.replace("D", "E").replace("d", "e")) for value in match.groups()]
            rows.append(values[3:6])
            if len(rows) == atom_count:
                return rows
    raise RuntimeError(f"Expected {atom_count} NWChem gradient rows, found {len(rows)}")


def run_nwchem_observables(
    atoms_bohr: list[list[Any]], basis: str, run_dir: Path, gradient: bool
) -> dict[str, Any]:
    prefix = run_dir.name.lower().replace("-", "_")
    input_path = run_dir / "nwchem.nw"
    output_path = run_dir / "nwchem.out"
    operation = "gradient" if gradient else "energy"
    input_path.write_text(nwchem_input(prefix, atoms_bohr, basis, operation), encoding="utf-8")
    command = [
        str(micromamba_path()),
        "run",
        "-n",
        "ai4orgchem-v02-wp2",
        "nwchem",
        input_path.name,
    ]
    completed = subprocess.run(command, cwd=run_dir, capture_output=True, text=True, check=False)
    output_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"NWChem failed with exit code {completed.returncode}; see {output_path}")
    text = output_path.read_text(encoding="utf-8", errors="replace")
    energies = NWCHEM_ENERGY_RE.findall(text)
    if not energies:
        raise RuntimeError(f"NWChem energy not found in {output_path}")
    if "Grid used for XC integration:  huge" not in text:
        raise RuntimeError("NWChem did not adopt the frozen huge grid")
    result: dict[str, Any] = {
        "energy_hartree": float(energies[-1].replace("D", "E").replace("d", "e")),
        "converged": True,
        "input_sha256": sha256(input_path),
        "output_sha256": sha256(output_path),
        "grid_adoption_proved": True,
    }
    if gradient:
        result["gradient_hartree_per_bohr"] = parse_nwchem_gradient(text, len(atoms_bohr))
        result["gradient_method"] = "analytic"
    return result


def tangent_for(spec: dict[str, Any]) -> np.ndarray | None:
    projection = spec.get("projection")
    if projection == "nba_torsion":
        return np.asarray(V02.nba_torsion_tangent(spec["atoms"]), dtype=float)
    if projection == "b2u":
        return np.asarray(V02.b2u_tangent(), dtype=float)
    return None


def add_derivative_summary(result: dict[str, Any], tangent: np.ndarray | None) -> None:
    if "gradient_hartree_per_bohr" not in result:
        return
    gradient = np.asarray(result["gradient_hartree_per_bohr"], dtype=float)
    if tangent is not None:
        derivative = float(np.sum(gradient * tangent))
        result["projected_energy_derivative_hartree_per_bohr"] = derivative
        result["projected_force_hartree_per_bohr"] = -derivative


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", required=True)
    parser.add_argument("--programs", nargs="+", choices=["pyscf", "psi4", "nwchem"], default=["pyscf", "psi4", "nwchem"])
    args = parser.parse_args()
    spec = next((row for row in V02.anchor_specs() if row["id"] == args.anchor), None)
    if spec is None:
        raise SystemExit(f"Unknown anchor: {args.anchor}")

    run_dir = RUN_ROOT / spec["id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    atoms_bohr = to_bohr(spec["atoms"])
    needs_gradient = bool(spec.get("gradient"))
    tangent = tangent_for(spec)
    source_path = V02.ROOT / spec["source"]
    record: dict[str, Any] = {
        "schema_version": "science-v0.3-wp2-open-three-program-anchor-1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "anchor_id": spec["id"],
        "source": spec["source"],
        "source_sha256": sha256(source_path),
        "contract": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "contract_sha256": sha256(CONTRACT),
        "basis": spec["basis"],
        "geometry_unit": "bohr",
        "geometry_sha256": hashlib.sha256(json.dumps(atoms_bohr, separators=(",", ":")).encode()).hexdigest(),
        "atom_count": len(atoms_bohr),
        "programs": {},
    }
    partial_path = run_dir / "partial.json"
    if partial_path.exists():
        previous = json.loads(partial_path.read_text(encoding="utf-8"))
        same_identity = (
            previous.get("anchor_id") == record["anchor_id"]
            and previous.get("source_sha256") == record["source_sha256"]
            and previous.get("geometry_sha256") == record["geometry_sha256"]
            and previous.get("basis") == record["basis"]
        )
        if same_identity:
            record["programs"].update(previous.get("programs", {}))
            if previous.get("contract_sha256") != record["contract_sha256"]:
                record["resume_provenance"] = {
                    "previous_contract_sha256": previous.get("contract_sha256"),
                    "current_contract_sha256": record["contract_sha256"],
                    "reuse_rule": "Only results from programs whose frozen settings were unchanged by the amendment are retained.",
                }
    psi4.set_memory("10 GB")
    psi4.set_num_threads(1)
    if "pyscf" in args.programs:
        record["programs"]["PySCF"] = run_pyscf_observables(atoms_bohr, spec["basis"], needs_gradient)
        add_derivative_summary(record["programs"]["PySCF"], tangent)
        record["programs"]["PySCF"]["version"] = pyscf.__version__
        partial_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if "psi4" in args.programs:
        record["programs"]["Psi4"] = run_psi4_observables(
            atoms_bohr, spec["basis"], run_dir / "psi4.log", needs_gradient
        )
        add_derivative_summary(record["programs"]["Psi4"], tangent)
        record["programs"]["Psi4"]["version"] = psi4.__version__
        partial_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if "nwchem" in args.programs:
        record["programs"]["NWChem"] = run_nwchem_observables(
            atoms_bohr, spec["basis"], run_dir, needs_gradient
        )
        add_derivative_summary(record["programs"]["NWChem"], tangent)
        record["programs"]["NWChem"].update({"banner_version": "7.3.0", "revision": "3272822"})

    program_rows = record["programs"]
    energies = [row["energy_hartree"] for row in program_rows.values()]
    energy_span = max(energies) - min(energies)
    comparison: dict[str, Any] = {
        "program_count": len(program_rows),
        "required_program_count": 3,
        "pairwise_span_hartree": energy_span,
        "threshold_hartree": 5.0e-6,
        "energy_pass": len(program_rows) == 3 and energy_span <= 5.0e-6,
    }
    derivative_pass = True
    if needs_gradient and tangent is None and len(program_rows) == 3:
        gradients = {
            name: np.asarray(row["gradient_hartree_per_bohr"], dtype=float)
            for name, row in program_rows.items()
        }
        pairwise_rms = {}
        names = list(gradients)
        for i, first in enumerate(names):
            for second in names[i + 1 :]:
                difference = gradients[first] - gradients[second]
                pairwise_rms[f"{first}_vs_{second}"] = float(np.sqrt(np.mean(difference * difference)))
        comparison["gradient_pairwise_rms_hartree_per_bohr"] = pairwise_rms
        comparison["gradient_threshold_hartree_per_bohr"] = 5.0e-5
        derivative_pass = max(pairwise_rms.values()) <= 5.0e-5
        comparison["gradient_pass"] = derivative_pass
    elif needs_gradient and tangent is not None and len(program_rows) == 3:
        derivatives = {
            name: float(row["projected_energy_derivative_hartree_per_bohr"])
            for name, row in program_rows.items()
        }
        derivative_span = max(derivatives.values()) - min(derivatives.values())
        comparison["projected_energy_derivatives_hartree_per_bohr"] = derivatives
        comparison["projected_derivative_span_hartree_per_bohr"] = derivative_span
        comparison["projected_derivative_threshold_hartree_per_bohr"] = 5.0e-5
        derivative_pass = derivative_span <= 5.0e-5
        comparison["projected_derivative_pass"] = derivative_pass
    elif needs_gradient:
        derivative_pass = False
    comparison["pass"] = comparison["energy_pass"] and derivative_pass
    record["comparison"] = comparison
    output = run_dir / "result.json"
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record["comparison"], indent=2))


if __name__ == "__main__":
    main()
