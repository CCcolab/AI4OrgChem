from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import pyscf
from pyscf import dft, gto, lib


def read_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    count = int(lines[0])
    rows = [line.split() for line in lines[2 : 2 + count]]
    if len(rows) != count:
        raise ValueError(f"Incomplete XYZ: {path}")
    return [row[0] for row in rows], np.asarray([[float(v) for v in row[1:4]] for row in rows])


def configure(mf: dft.rks.RKS | dft.uks.UKS) -> None:
    mf.xc = "b3lypg"
    mf.grids.atom_grid = (75, 302)
    mf.grids.prune = dft.gen_grid.nwchem_prune
    mf.conv_tol = 1e-9
    mf.max_cycle = 300
    mf.chkfile = None


def rotated_density(coeff: np.ndarray, nocc: int, theta: float) -> tuple[np.ndarray, np.ndarray]:
    homo, lumo = nocc - 1, nocc
    ca = coeff.copy()
    cb = coeff.copy()
    for target, sign in ((ca, 1.0), (cb, -1.0)):
        h = coeff[:, homo].copy()
        l = coeff[:, lumo].copy()
        target[:, homo] = np.cos(theta) * h + sign * np.sin(theta) * l
        target[:, lumo] = -sign * np.sin(theta) * h + np.cos(theta) * l
    return ca[:, :nocc] @ ca[:, :nocc].T, cb[:, :nocc] @ cb[:, :nocc].T


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--species", choices=["A", "C"], required=True)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.N not in (16, 32):
        raise ValueError("WP4-B source-geometry BS pilot is bounded to N=16 and N=32")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    lib.num_threads(args.threads)
    atoms, coords = read_xyz(args.input)
    mol = gto.M(
        atom=list(zip(atoms, coords.tolist())), unit="Angstrom", basis="6-31g*",
        charge=0, spin=0, symmetry=False, verbose=3, max_memory=6000,
    )
    started = time.perf_counter()
    rks = dft.RKS(mol)
    configure(rks)
    rks_energy = float(rks.kernel())
    if not rks.converged:
        raise RuntimeError("Reference RKS did not converge")
    nocc = mol.nelectron // 2
    trials: list[dict[str, object]] = []
    # N=16 retains the three-angle sensitivity check.  For N=32 the strongest
    # registered perturbation is sufficient for the paired pilot: collapse of
    # 0.40 rad to the RKS state subsumes the weaker perturbations and avoids two
    # redundant large-system UKS calculations.
    theta_schedule = (0.40,) if args.N == 32 else (0.10, 0.20, 0.40)
    for theta in theta_schedule:
        dm_a, dm_b = rotated_density(rks.mo_coeff, nocc, theta)
        uks = dft.UKS(mol)
        configure(uks)
        energy = float(uks.kernel(dm0=(dm_a, dm_b)))
        s2, multiplicity = uks.spin_square()
        trials.append({
            "theta_rad": theta,
            "converged": bool(uks.converged),
            "energy_hartree": energy,
            "delta_from_rks_kcal_mol": (energy - rks_energy) * 627.5094740631,
            "s2": float(s2),
            "effective_multiplicity": float(multiplicity),
        })
    converged = [row for row in trials if row["converged"]]
    lowest = min(converged, key=lambda row: float(row["energy_hartree"])) if converged else None
    result = {
        "schema_version": "science-v0.3-wp4b-bs-check-1",
        "N": args.N,
        "species": args.species,
        "geometry_role": "published_source_geometry",
        "input": str(args.input),
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "program": "PySCF",
        "program_version": pyscf.__version__,
        "python": platform.python_version(),
        "method": "B3LYPG/6-31G(d)",
        "grid": {"radial": 75, "angular": 302, "pruning": "nwchem_prune"},
        "rks_energy_hartree": rks_energy,
        "rks_converged": bool(rks.converged),
        "trials": trials,
        "initialization_policy": "N16: 0.10/0.20/0.40 rad; N32: strongest registered 0.40 rad perturbation",
        "lowest_converged_uks": lowest,
        "interpretation_rule": "A lower converged UKS solution with nonzero <S^2> flags closed-shell sensitivity; no automatic aromaticity label follows.",
        "elapsed_seconds": time.perf_counter() - started,
        "threads": args.threads,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
