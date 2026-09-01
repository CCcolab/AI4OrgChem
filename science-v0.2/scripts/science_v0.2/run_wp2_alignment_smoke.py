from __future__ import annotations

import hashlib
import json
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psi4
import pyscf
from pyscf import dft, gto


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/processed/p09_benzene_G_DSI3_smoke_v0.1.json"
OUTPUT = ROOT / "data/science_v0.2/raw/wp2/wp2_functional_alignment_smoke.json"
TOLERANCE = 5.0e-6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    atoms = source["optimized_G_geometry"]["atoms_angstrom"]
    atom_spec = [(row[0], tuple(float(x) for x in row[1:4])) for row in atoms]

    mol = gto.M(atom=atom_spec, basis="6-31g*", unit="Angstrom", charge=0, spin=0, cart=False, symmetry=False)
    mf = dft.RKS(mol)
    mf.xc = "B3LYPG"
    mf.grids.level = 3
    mf.conv_tol = 1.0e-10
    mf.max_cycle = 200
    mf.verbose = 0
    pyscf_energy = float(mf.kernel())

    geometry = ["0 1", "symmetry c1", "no_reorient", "no_com"]
    geometry.extend(f"{s} {x:.16f} {y:.16f} {z:.16f}" for s, (x, y, z) in atom_spec)
    psi4.core.clean()
    psi4.core.set_output_file(str(OUTPUT.with_suffix(".psi4.log")), False)
    psi4.set_memory("2 GB")
    psi4.set_num_threads(1)
    psi4_mol = psi4.geometry("\n".join(geometry))
    psi4.set_options(
        {
            "basis": "6-31G*",
            "reference": "RKS",
            "puream": True,
            "scf_type": "DIRECT",
            "e_convergence": 10,
            "d_convergence": 9,
            "maxiter": 200,
            "dft_radial_points": 75,
            "dft_spherical_points": 302,
            "dft_pruning_scheme": "ROBUST",
        }
    )
    psi4_energy = float(psi4.energy("b3lyp", molecule=psi4_mol))
    delta = psi4_energy - pyscf_energy

    record = {
        "schema_version": "science-v0.2-wp2-functional-alignment-smoke-1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "anchor_id": "WP2-P09-BENZENE-G-E",
        "science_target_values_used_for_tuning": False,
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "geometry_sha256": source["optimized_G_geometry"]["geometry_sha256"],
        "charge": 0,
        "multiplicity": 1,
        "basis": "6-31G(d), spherical",
        "programs": {
            "PySCF": {
                "version": pyscf.__version__,
                "functional": "B3LYPG",
                "grid": "PySCF level 3",
                "energy_hartree": pyscf_energy,
                "converged": bool(mf.converged),
            },
            "Psi4": {
                "version": psi4.__version__,
                "functional": "B3LYP",
                "grid": "75 radial x 302 spherical, ROBUST pruning",
                "energy_hartree": psi4_energy,
            },
            "ORCA": {
                "available": shutil.which("orca") is not None,
                "license_bypass_attempted": False,
            },
        },
        "comparison": {
            "psi4_minus_pyscf_hartree": delta,
            "absolute_difference_hartree": abs(delta),
            "preregistered_tolerance_hartree": TOLERANCE,
            "passes_open_program_alignment": bool(abs(delta) <= TOLERANCE),
        },
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
    }
    OUTPUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record["comparison"], indent=2))


if __name__ == "__main__":
    main()
