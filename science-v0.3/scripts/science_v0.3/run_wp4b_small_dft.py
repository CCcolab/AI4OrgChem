from __future__ import annotations

import argparse
import faulthandler
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
from pyscf import dft, gto, lib
from pyscf.data import nist
from pyscf.geomopt.geometric_solver import optimize
from pyscf.hessian import thermo


def read_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    count = int(lines[0])
    rows = [line.split() for line in lines[2 : 2 + count]]
    if len(rows) != count:
        raise ValueError(f"Incomplete XYZ: {path}")
    return [row[0] for row in rows], np.asarray([[float(v) for v in row[1:4]] for row in rows])


def write_xyz(path: Path, atoms: list[str], coords: np.ndarray, comment: str) -> None:
    lines = [str(len(atoms)), comment]
    lines.extend(
        f"{atom:2s} {xyz[0]: .10f} {xyz[1]: .10f} {xyz[2]: .10f}"
        for atom, xyz in zip(atoms, coords)
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def configured_rks(mol: gto.Mole, *, geometry_stage: bool = False) -> dft.rks.RKS:
    mf = dft.RKS(mol)
    mf.xc = "b3lypg"
    mf.grids.atom_grid = (50, 194) if geometry_stage else (75, 302)
    mf.grids.prune = dft.gen_grid.nwchem_prune
    mf.conv_tol = 1e-7 if geometry_stage else 1e-9
    mf.max_cycle = 300
    mf.chkfile = None
    if geometry_stage:
        mf = mf.density_fit()
    return mf


def xtb_preopt(input_path: Path, log_path: Path, threads: int) -> tuple[list[str], np.ndarray, float]:
    executable = shutil.which("xtb")
    if executable is None:
        raise RuntimeError("xtb executable is not available in the active environment")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="wp4b_xtb_") as tmp:
        work = Path(tmp)
        target = work / "input.xyz"
        shutil.copy2(input_path, target)
        completed = subprocess.run(
            [
                executable,
                str(target),
                "--gfn", "2",
                "--opt", "normal",
                "--chrg", "0",
                "--uhf", "0",
                "--parallel", str(threads),
            ],
            cwd=work,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path.write_text(completed.stdout, encoding="utf-8")
        optimized = work / "xtbopt.xyz"
        if completed.returncode != 0 or not optimized.exists():
            raise RuntimeError(f"GFN2-xTB pre-optimization failed; see {log_path}")
        atoms, coords = read_xyz(optimized)
    return atoms, coords, time.perf_counter() - started


def broken_symmetry_single_point(mol: gto.Mole, rks: dft.rks.RKS) -> dict[str, object]:
    nocc = mol.nelectron // 2
    coeff = rks.mo_coeff
    homo, lumo = nocc - 1, nocc
    theta = 0.20
    ca = coeff.copy()
    cb = coeff.copy()
    for target, sign in ((ca, 1.0), (cb, -1.0)):
        h = coeff[:, homo].copy()
        l = coeff[:, lumo].copy()
        target[:, homo] = np.cos(theta) * h + sign * np.sin(theta) * l
        target[:, lumo] = -sign * np.sin(theta) * h + np.cos(theta) * l
    dm_a = ca[:, :nocc] @ ca[:, :nocc].T
    dm_b = cb[:, :nocc] @ cb[:, :nocc].T
    uks = dft.UKS(mol)
    uks.xc = "b3lypg"
    uks.grids.atom_grid = (75, 302)
    uks.grids.prune = dft.gen_grid.nwchem_prune
    uks.conv_tol = 1e-9
    uks.max_cycle = 300
    uks.chkfile = None
    energy = float(uks.kernel(dm0=(dm_a, dm_b)))
    s2, multiplicity = uks.spin_square()
    return {
        "attempted": True,
        "converged": bool(uks.converged),
        "energy_hartree": energy,
        "delta_from_rks_kcal_mol": (energy - float(rks.e_tot)) * 627.5094740631,
        "s2": float(s2),
        "effective_multiplicity": float(multiplicity),
        "initial_homo_lumo_rotation_rad": theta,
        "scope": "single-point stability diagnostic at the optimized closed-shell geometry"
    }


def main() -> None:
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--species", choices=list("ABCD"), required=True)
    parser.add_argument("--source", choices=["source", "etkdg", "auditbest", "crest"], required=True)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--maxsteps", type=int, default=150)
    parser.add_argument(
        "--energy-only",
        action="store_true",
        help="Stop after optimized-geometry final electronic energy; used for conformer selection.",
    )
    args = parser.parse_args()
    if args.N not in (8, 10, 16, 18, 32, 34):
        raise ValueError("N is outside the frozen WP4-B paired pilot")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    lib.num_threads(args.threads)
    xtb_log = args.output.with_suffix(".xtb.log")
    opt_xyz = args.output.with_suffix(".optimized.xyz")
    checkpoint = args.output.with_suffix(".electronic.json")
    if opt_xyz.exists():
        atoms, coords = read_xyz(opt_xyz)
        xtb_seconds = None
        resumed_from_optimized = True
    else:
        atoms, coords, xtb_seconds = xtb_preopt(args.input, xtb_log, args.threads)
        resumed_from_optimized = False
    mol = gto.M(
        atom=list(zip(atoms, coords.tolist())),
        unit="Angstrom",
        basis="6-31g*",
        charge=0,
        spin=0,
        symmetry=False,
        verbose=4,
        max_memory=6000,
    )
    started = time.perf_counter()
    if resumed_from_optimized:
        optimized = mol
    else:
        initial_mf = configured_rks(mol, geometry_stage=True)
        optimized = optimize(
            initial_mf,
            maxsteps=args.maxsteps,
            convergence_energy=1e-6,
            convergence_grms=3e-4,
            convergence_gmax=4.5e-4,
            convergence_drms=1.2e-3,
            convergence_dmax=1.8e-3,
        )
        write_xyz(
            opt_xyz,
            atoms,
            optimized.atom_coords(unit="Angstrom"),
            "WP4-B PySCF geometry checkpoint; DF-B3LYPG/6-31G(d)",
        )
    final_mf = configured_rks(optimized)
    electronic = float(final_mf.kernel())
    checkpoint.write_text(
        json.dumps(
            {
                "electronic_hartree": electronic,
                "scf_converged": bool(final_mf.converged),
                "grid": [75, 302],
                "method": "B3LYPG/6-31G(d)",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"ELECTRONIC_CHECKPOINT={checkpoint}", flush=True)
    if args.energy_only:
        candidate = {
            "schema_version": "science-v0.3-wp4b-conformer-candidate-1",
            "N": args.N,
            "series": "4n" if args.N % 4 == 0 else "4n+2",
            "species": args.species,
            "conformer_source": args.source,
            "input": str(args.input),
            "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
            "program": "PySCF",
            "program_version": __import__("pyscf").__version__,
            "method": "B3LYPG/6-31G(d)",
            "geometry_acceleration": "GFN2-xTB preopt + density-fitted B3LYPG/6-31G(d) 50x194 optimization",
            "final_grid": {"radial": 75, "angular": 302, "pruning": "nwchem_prune"},
            "optimization_converged": True,
            "resumed_from_optimized_checkpoint": resumed_from_optimized,
            "scf_converged": bool(final_mf.converged),
            "electronic_hartree": electronic,
            "optimized_xyz": str(opt_xyz),
            "frequency_status": "NOT_RUN_CONFORMER_SCREEN",
            "elapsed_seconds": time.perf_counter() - started,
            "threads": args.threads,
        }
        args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(candidate, ensure_ascii=False, indent=2), flush=True)
        return
    hessian = final_mf.Hessian().kernel()
    vibration = thermo.harmonic_analysis(optimized, hessian)
    freq_cm = np.asarray(vibration["freq_wavenumber"])
    real_freq = np.real(freq_cm)
    imag_magnitudes = [float(abs(x.imag)) for x in freq_cm if abs(x.imag) > 1e-6]
    negative_real = [float(x) for x in real_freq if x < -10.0]
    imaginary_count = len(imag_magnitudes) + len(negative_real)
    positive_cm = [float(x.real) for x in freq_cm if abs(x.imag) <= 1e-10 and x.real > 0]
    hartree_to_wavenumber = nist.HARTREE2J / (nist.PLANCK * nist.LIGHT_SPEED_SI * 100.0)
    zpve = 0.5 * sum(positive_cm) / hartree_to_wavenumber
    coords_opt = optimized.atom_coords(unit="Angstrom")
    write_xyz(opt_xyz, atoms, coords_opt, f"WP4-B PySCF B3LYPG/6-31G(d); E0={electronic + zpve:.12f}")
    bs_required = args.N % 4 == 0 and args.species in {"A", "C"}
    bs = broken_symmetry_single_point(optimized, final_mf) if bs_required else {"attempted": False}
    result = {
        "schema_version": "science-v0.3-wp4b-dft-result-2",
        "N": args.N,
        "series": "4n" if args.N % 4 == 0 else "4n+2",
        "species": args.species,
        "conformer_source": args.source,
        "input": str(args.input),
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "program": "PySCF",
        "program_version": __import__("pyscf").__version__,
        "python": platform.python_version(),
        "host": os.uname().nodename,
        "method": "B3LYPG/6-31G(d)",
        "grid": {"radial": 75, "angular": 302, "pruning": "nwchem_prune"},
        "geometry_acceleration": "GFN2-xTB preopt + density-fitted B3LYPG/6-31G(d) 50x194 optimization",
        "xtb_elapsed_seconds": xtb_seconds,
        "xtb_log": str(xtb_log),
        "optimization_converged": True,
        "resumed_from_optimized_checkpoint": resumed_from_optimized,
        "scf_converged": bool(final_mf.converged),
        "electronic_hartree": electronic,
        "zpve_hartree": zpve,
        "zpve_conversion": "0.5*sum(positive harmonic wavenumbers)/219474.631... cm^-1 per hartree",
        "e0_hartree": electronic + zpve,
        "frequency_count": int(freq_cm.size),
        "minimum": imaginary_count == 0,
        "imaginary_frequency_count": imaginary_count,
        "imaginary_magnitudes_cm_minus_1": imag_magnitudes,
        "negative_real_frequencies_cm_minus_1": negative_real,
        "lowest_real_frequency_cm_minus_1": float(np.min(real_freq)) if real_freq.size else None,
        "broken_symmetry": bs,
        "optimized_xyz": str(opt_xyz),
        "elapsed_seconds": time.perf_counter() - started,
        "threads": args.threads,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
