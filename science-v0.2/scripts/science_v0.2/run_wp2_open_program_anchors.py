from __future__ import annotations

import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import psi4
import pyscf
from pyscf import dft, gto


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data/science_v0.2/raw/wp2/wp2_open_program_anchors.json"
HARTREE_TO_KCAL = 627.5094740631
BOHR_TO_ANGSTROM = 0.52917721092
FINITE_DIFFERENCE_STEP_BOHR = 1.0e-3


def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def d3h_atoms(mean_cc: float, delta: float, ch_length: float) -> list[list[Any]]:
    edges = [mean_cc - delta, mean_cc + delta] * 3
    angles = np.deg2rad([120.0, 180.0, 240.0, 300.0, 0.0, 60.0])
    carbons = np.zeros((6, 2))
    for i in range(5):
        carbons[i + 1] = carbons[i] + edges[i] * np.array([np.cos(angles[i]), np.sin(angles[i])])
    carbons -= np.mean(carbons, axis=0)
    radial = carbons / np.linalg.norm(carbons, axis=1)[:, None]
    hydrogens = carbons + ch_length * radial
    return [*[ ["C", float(x), float(y), 0.0] for x, y in carbons],
            *[ ["H", float(x), float(y), 0.0] for x, y in hydrogens]]


def nba_torsion_tangent(atoms: list[list[Any]]) -> np.ndarray:
    xyz = np.asarray([row[1:4] for row in atoms], dtype=float)
    # Frozen P03 protocol: rotation axis [0, 6], rotating atoms
    # [1,2,3,4,5,14,15,16,17,18], zero-based.
    origin = xyz[0]
    axis = xyz[6] - origin
    axis /= np.linalg.norm(axis)
    tangent = np.zeros_like(xyz)
    for i in [1, 2, 3, 4, 5, 14, 15, 16, 17, 18]:
        tangent[i] = np.cross(axis, xyz[i] - origin)
    norm = np.linalg.norm(tangent)
    if norm < 1.0e-12:
        raise ValueError("NBA torsion tangent is singular")
    return tangent / norm


def b2u_tangent() -> np.ndarray:
    modes = load("configs/science_v0.2/wp3_symmetry_mode_seeds.json")
    row = next(item for item in modes["modes"] if item["mode_id"] == "B2u_BLA")
    tangent = np.asarray(row["cartesian_displacement_per_unit_Q"], dtype=float)
    return tangent / np.linalg.norm(tangent)


def anchor_specs() -> list[dict[str, Any]]:
    p03_rel = "data/processed/p03_parent_nba_relaxed_pes_evidence_v0.1.json"
    p08_rel = "data/processed/p08_butadiene_gl2014_evidence_v0.1.json"
    p09b_rel = "data/processed/p09_benzene_G_DSI3_smoke_v0.1.json"
    p09c_rel = "data/processed/p09_cyclobutadiene_G_DSI_VDE_v0.1.json"
    p10_rel = "data/processed/p10_benzene_nuclear_repulsion_v0.1.json"
    p11_rel = "data/processed/p11_furan_LDE_v0.1.json"
    p03, p08, p09b, p09c, p10, p11 = map(load, [p03_rel, p08_rel, p09b_rel, p09c_rel, p10_rel, p11_rel])
    scan = p10["ordinary_RKS_BLA_scan"]
    p10_q0 = d3h_atoms(scan["mean_CC_angstrom"], 0.0, scan["fixed_CH_angstrom"])
    p10_qplus = d3h_atoms(scan["mean_CC_angstrom"], 0.01, scan["fixed_CH_angstrom"])
    return [
        {"id": "WP2-P03-NBA-000-EF", "source": p03_rel, "atoms": p03["points"]["0.0"]["geometry"]["atoms"], "basis": "6-311G**", "gradient": True, "projection": "nba_torsion"},
        {"id": "WP2-P03-NBA-060-E", "source": p03_rel, "atoms": p03["points"]["60.0"]["geometry"]["atoms"], "basis": "6-311G**", "gradient": False},
        {"id": "WP2-P08-BUTADIENE-G-EG", "source": p08_rel, "atoms": p08["ground_geometry"]["atoms"], "basis": "6-31G*", "gradient": True},
        {"id": "WP2-P09-BENZENE-G-E", "source": p09b_rel, "atoms": p09b["optimized_G_geometry"]["atoms_angstrom"], "basis": "6-31G*", "gradient": False},
        {"id": "WP2-P09-CBD-G-E", "source": p09c_rel, "atoms": p09c["optimized_G_geometry"]["atoms_angstrom"], "basis": "6-31G*", "gradient": False},
        {"id": "WP2-P10-BENZENE-B2U-Q0-EF", "source": p10_rel, "atoms": p10_q0, "basis": "6-31G*", "gradient": True, "projection": "b2u"},
        {"id": "WP2-P10-BENZENE-B2U-QPLUS-E", "source": p10_rel, "atoms": p10_qplus, "basis": "6-31G*", "gradient": False, "delta_angstrom": 0.01},
        {"id": "WP2-P11-FURAN-G-E", "source": p11_rel, "atoms": p11["G"]["atoms_angstrom"], "basis": "6-31G*", "gradient": False},
    ]


def pyscf_energy(atoms: list[list[Any]], basis: str) -> tuple[float, bool]:
    mol = gto.M(atom=atoms, basis=basis.lower(), unit="Angstrom", charge=0, spin=0, cart=False, symmetry=False)
    mf = dft.RKS(mol)
    mf.xc = "B3LYPG"
    mf.grids.level = 3
    mf.conv_tol = 1.0e-10
    mf.max_cycle = 200
    mf.verbose = 0
    return float(mf.kernel()), bool(mf.converged)


def run_pyscf(
    atoms: list[list[Any]], basis: str, gradient: bool, projection: str | None
) -> tuple[float, np.ndarray | None, bool, float | None]:
    energy, converged = pyscf_energy(atoms, basis)
    if not gradient:
        return energy, None, converged, None
    if projection:
        tangent = nba_torsion_tangent(atoms) if projection == "nba_torsion" else b2u_tangent()
        plus, plus_converged = pyscf_energy(displaced(atoms, tangent, FINITE_DIFFERENCE_STEP_BOHR), basis)
        minus, minus_converged = pyscf_energy(displaced(atoms, tangent, -FINITE_DIFFERENCE_STEP_BOHR), basis)
        derivative = (plus - minus) / (2.0 * FINITE_DIFFERENCE_STEP_BOHR)
        return energy, None, converged and plus_converged and minus_converged, derivative
    mol = gto.M(atom=atoms, basis=basis.lower(), unit="Angstrom", charge=0, spin=0, cart=False, symmetry=False)
    mf = dft.RKS(mol)
    mf.xc = "B3LYPG"
    mf.grids.level = 3
    mf.conv_tol = 1.0e-10
    mf.max_cycle = 200
    mf.verbose = 0
    mf.kernel()
    grad = np.asarray(mf.nuc_grad_method().kernel(), dtype=float)
    return energy, grad, converged and bool(mf.converged), None


def psi4_molecule(atoms: list[list[Any]]):
    geometry = ["0 1", "symmetry c1", "no_reorient", "no_com"]
    geometry.extend(f"{row[0]} {float(row[1]):.16f} {float(row[2]):.16f} {float(row[3]):.16f}" for row in atoms)
    return psi4.geometry("\n".join(geometry))


def psi4_direct_energy(atoms: list[list[Any]], basis: str) -> float:
    psi4.core.clean()
    mol = psi4_molecule(atoms)
    psi4.set_options({
        "basis": basis,
        "reference": "RKS",
        "puream": True,
        "scf_type": "DIRECT",
        "e_convergence": 10,
        "d_convergence": 9,
        "maxiter": 200,
        "dft_radial_points": 75,
        "dft_spherical_points": 302,
        "dft_pruning_scheme": "ROBUST",
    })
    return float(psi4.energy("b3lyp", molecule=mol))


def displaced(atoms: list[list[Any]], direction: np.ndarray, signed_step_bohr: float) -> list[list[Any]]:
    xyz = np.asarray([row[1:4] for row in atoms], dtype=float)
    moved = xyz + signed_step_bohr * BOHR_TO_ANGSTROM * direction
    return [[row[0], *map(float, moved[i])] for i, row in enumerate(atoms)]


def run_psi4(
    atoms: list[list[Any]], basis: str, gradient: bool, log: Path, projection: str | None
) -> tuple[float, np.ndarray | None, float | None]:
    psi4.core.clean()
    psi4.core.set_output_file(str(log), False)
    energy = psi4_direct_energy(atoms, basis)
    if not gradient:
        return energy, None, None
    if projection:
        tangent = nba_torsion_tangent(atoms) if projection == "nba_torsion" else b2u_tangent()
        plus = psi4_direct_energy(displaced(atoms, tangent, FINITE_DIFFERENCE_STEP_BOHR), basis)
        minus = psi4_direct_energy(displaced(atoms, tangent, -FINITE_DIFFERENCE_STEP_BOHR), basis)
        derivative = (plus - minus) / (2.0 * FINITE_DIFFERENCE_STEP_BOHR)
        return energy, None, derivative
    # Psi4 analytic DFT gradients can invoke a DF response backend even when
    # the SCF energy uses DIRECT. A numerical gradient forces every displaced
    # point through the exact DIRECT energy path frozen above.
    mol = psi4_molecule(atoms)
    matrix, wavefunction = psi4.gradient("b3lyp", molecule=mol, return_wfn=True, dertype=0)
    return float(wavefunction.energy()), np.asarray(matrix, dtype=float), None


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    psi4.set_memory("3 GB")
    psi4.set_num_threads(1)
    rows = []
    for spec in anchor_specs():
        projection = spec.get("projection")
        py_e, py_g, py_conv, py_projected = run_pyscf(
            spec["atoms"], spec["basis"], spec["gradient"], projection
        )
        ps_e, ps_g, ps_projected = run_psi4(
            spec["atoms"], spec["basis"], spec["gradient"],
            OUTPUT.parent / f"{spec['id']}.psi4.log", projection,
        )
        row: dict[str, Any] = {
            "anchor_id": spec["id"],
            "source": spec["source"],
            "source_sha256": sha(spec["source"]),
            "basis": spec["basis"],
            "atom_count": len(spec["atoms"]),
            "PySCF": {"energy_hartree": py_e, "converged": py_conv},
            "Psi4": {"energy_hartree": ps_e},
            "comparison": {
                "psi4_minus_pyscf_hartree": ps_e - py_e,
                "absolute_energy_difference_hartree": abs(ps_e - py_e),
                "energy_pass": abs(ps_e - py_e) <= 5.0e-6,
            },
        }
        if "delta_angstrom" in spec:
            row["delta_angstrom"] = spec["delta_angstrom"]
        if py_g is not None and ps_g is not None:
            diff = ps_g - py_g
            row["comparison"]["gradient_rms_difference_hartree_per_bohr"] = float(np.sqrt(np.mean(diff * diff)))
            row["comparison"]["gradient_pass"] = bool(row["comparison"]["gradient_rms_difference_hartree_per_bohr"] <= 5.0e-5)
        if projection and py_projected is not None and ps_projected is not None:
            row["projected_gradient"] = {
                "definition": projection,
                "PySCF_method": "central finite difference of full-integral energies",
                "Psi4_method": "central finite difference of exact DIRECT energies",
                "finite_difference_step_bohr": FINITE_DIFFERENCE_STEP_BOHR,
                "PySCF_hartree_per_bohr": py_projected,
                "Psi4_hartree_per_bohr": ps_projected,
                "absolute_difference_hartree_per_bohr": abs(ps_projected - py_projected),
                "pass": abs(ps_projected - py_projected) <= 5.0e-5,
            }
        rows.append(row)
        print(spec["id"], row["comparison"])

    by_id = {row["anchor_id"]: row for row in rows}
    relative_pairs = []
    for name, first, second in [
        ("P03_60_minus_0", "WP2-P03-NBA-000-EF", "WP2-P03-NBA-060-E"),
        ("P10_qplus_minus_q0", "WP2-P10-BENZENE-B2U-Q0-EF", "WP2-P10-BENZENE-B2U-QPLUS-E"),
    ]:
        py = (by_id[second]["PySCF"]["energy_hartree"] - by_id[first]["PySCF"]["energy_hartree"]) * HARTREE_TO_KCAL
        ps = (by_id[second]["Psi4"]["energy_hartree"] - by_id[first]["Psi4"]["energy_hartree"]) * HARTREE_TO_KCAL
        relative_pairs.append({"pair": name, "PySCF_kcal_mol": py, "Psi4_kcal_mol": ps, "absolute_difference_kcal_mol": abs(ps - py), "pass": abs(ps - py) <= 0.05})

    checks = [r["comparison"]["energy_pass"] for r in rows]
    checks.extend(r["comparison"].get("gradient_pass", True) for r in rows)
    checks.extend(r.get("projected_gradient", {}).get("pass", True) for r in rows)
    checks.extend(r["pass"] for r in relative_pairs)
    record = {
        "schema_version": "science-v0.2-wp2-open-program-anchors-1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "science_target_values_used_for_tuning": False,
        "programs": {"PySCF": pyscf.__version__, "Psi4": psi4.__version__, "ORCA_available": shutil.which("orca") is not None},
        "method_identity": {
            "PySCF": "B3LYPG analytic gradient",
            "Psi4": "B3LYP exact DIRECT energies; projected/full gradients by finite difference",
            "density_fitting": False,
            "smoke_record": "data/science_v0.2/raw/wp2/wp2_functional_alignment_smoke.json",
        },
        "anchors": rows,
        "relative_energy_pairs": relative_pairs,
        "open_program_lane_pass": bool(all(checks)),
        "three_program_core_contract_pass": False,
        "three_program_core_contract_reason": "ORCA is not available in the licensed local environment; no substitute is treated as ORCA-equivalent.",
    }
    OUTPUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"open_program_lane_pass": record["open_program_lane_pass"], "orca_available": record["programs"]["ORCA_available"]}, indent=2))


if __name__ == "__main__":
    main()
