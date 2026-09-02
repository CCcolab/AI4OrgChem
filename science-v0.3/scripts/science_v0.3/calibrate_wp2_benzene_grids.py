from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psi4
import pyscf
from pyscf import dft, gto


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/processed/p09_benzene_G_DSI3_smoke_v0.1.json"
OUTPUT = ROOT / "runs/science_v0.3/wp2/nwchem_smoke/benzene_high_grid_calibration.json"
BOHR_TO_ANGSTROM = 0.52917721092


def atoms_bohr() -> list[list[object]]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = payload["optimized_G_geometry"]["atoms_angstrom"]
    return [[row[0], *(float(value) / BOHR_TO_ANGSTROM for value in row[1:4])] for row in rows]


def pyscf_energy(atoms: list[list[object]], grid: str) -> tuple[float, bool, int]:
    mol = gto.M(
        atom=atoms,
        basis="6-31g*",
        unit="Bohr",
        charge=0,
        spin=0,
        cart=False,
        symmetry=False,
        verbose=0,
    )
    mf = dft.RKS(mol)
    mf.xc = "B3LYPG"
    if grid == "level3":
        mf.grids.level = 3
    elif grid == "nwchem_huge_shape":
        mf.grids.atom_grid = {"C": (300, 1454), "H": (300, 1202)}
        mf.grids.prune = dft.gen_grid.nwchem_prune
    else:
        raise ValueError(grid)
    mf.conv_tol = 1.0e-10
    mf.max_cycle = 200
    energy = float(mf.kernel())
    return energy, bool(mf.converged), int(mf.grids.coords.shape[0])


def psi4_energy(atoms: list[list[object]], radial: int, spherical: int) -> float:
    psi4.core.clean()
    geometry = ["0 1", "symmetry c1", "no_reorient", "no_com", "units bohr"]
    geometry.extend(
        f"{row[0]} {float(row[1]):.16f} {float(row[2]):.16f} {float(row[3]):.16f}"
        for row in atoms
    )
    mol = psi4.geometry("\n".join(geometry))
    psi4.set_options(
        {
            "basis": "6-31G*",
            "reference": "RKS",
            "puream": True,
            "scf_type": "DIRECT",
            "df_scf_guess": False,
            "ints_tolerance": 1.0e-12,
            "e_convergence": 10,
            "d_convergence": 9,
            "maxiter": 200,
            "dft_radial_points": radial,
            "dft_spherical_points": spherical,
            "dft_pruning_scheme": "ROBUST",
        }
    )
    return float(psi4.energy("b3lyp", molecule=mol))


def main() -> None:
    atoms = atoms_bohr()
    psi4.set_memory("5 GB")
    psi4.set_num_threads(1)
    psi4.core.set_output_file(str(OUTPUT.with_suffix(".psi4.log")), False)
    py_level3, py_level3_converged, py_level3_points = pyscf_energy(atoms, "level3")
    py_high, py_high_converged, py_high_points = pyscf_energy(atoms, "nwchem_huge_shape")
    ps_baseline = psi4_energy(atoms, 75, 302)
    ps_high = psi4_energy(atoms, 300, 1454)
    nwchem_high = -232.243821864982
    payload = {
        "schema_version": "science-v0.3-wp2-benzene-grid-calibration-1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "geometry_unit_internal": "bohr",
        "bohr_to_angstrom_constant": BOHR_TO_ANGSTROM,
        "method": "Gaussian-style B3LYP/6-31G(d), spherical, no density fitting",
        "programs": {
            "PySCF": {
                "version": pyscf.__version__,
                "level3": {
                    "energy_hartree": py_level3,
                    "converged": py_level3_converged,
                    "retained_grid_points": py_level3_points,
                },
                "nwchem_huge_shape": {
                    "energy_hartree": py_high,
                    "converged": py_high_converged,
                    "retained_grid_points": py_high_points,
                    "atom_grid": {"C": [300, 1454], "H": [300, 1202]},
                    "pruning": "PySCF nwchem_prune",
                },
            },
            "Psi4": {
                "version": psi4.__version__,
                "75x302_robust": {"energy_hartree": ps_baseline},
                "300x1454_robust": {"energy_hartree": ps_high},
            },
            "NWChem": {
                "banner_version": "7.3.0",
                "revision": "3272822",
                "huge_default": {
                    "energy_hartree": nwchem_high,
                    "grid": "C 300x1454; H 300x1202; NWChem pruning; Erf1 weights",
                },
            },
        },
        "comparisons_hartree": {
            "pyscf_high_minus_nwchem_high": py_high - nwchem_high,
            "psi4_high_minus_nwchem_high": ps_high - nwchem_high,
            "psi4_high_minus_pyscf_high": ps_high - py_high,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["comparisons_hartree"], indent=2))


if __name__ == "__main__":
    main()
