from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

from pyscf import dft, gto, mcscf, mrpt, scf

from wp1_geometry import d2h_geometry, d4h_geometry


BOHR_ANGSTROM = 0.529177210903
HARTREE_TO_KCAL_MOL = 627.5094740631


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_molecule(rows: list[list[Any]], basis: str, spin: int, memory_mb: int, verbose: int = 4) -> gto.Mole:
    mol = gto.Mole()
    mol.atom = [(row[0], tuple(float(x) for x in row[1:4])) for row in rows]
    mol.unit = "Angstrom"
    mol.charge = 0
    mol.spin = spin
    mol.basis = basis
    mol.symmetry = False
    mol.max_memory = memory_mb
    mol.verbose = verbose
    mol.build()
    return mol


def run_rks(rows: list[list[Any]], settings: dict[str, Any], memory_mb: int, dm0: np.ndarray | None = None):
    mol = make_molecule(rows, settings["basis"], 0, memory_mb)
    mf = dft.RKS(mol)
    mf.xc = settings["functional"]
    mf.grids.level = int(settings["grid_level"])
    mf.conv_tol = float(settings["scf_tolerance_hartree"])
    mf.max_cycle = int(settings["maximum_cycles"])
    mf.chkfile = None
    energy = float(mf.kernel(dm0=dm0))
    if not mf.converged:
        mf = mf.newton()
        mf.conv_tol = float(settings["scf_tolerance_hartree"])
        mf.max_cycle = int(settings["maximum_cycles"])
        energy = float(mf.kernel(mo_coeff=mf.mo_coeff, mo_occ=mf.mo_occ))
    return mol, mf, energy


def optimize_endpoint(kind: str, initial: list[float], settings: dict[str, Any], memory_mb: int) -> dict[str, Any]:
    geometry_function = d2h_geometry if kind == "D2h" else d4h_geometry
    bounds = settings[f"{kind}_bounds_angstrom"]
    evaluations: list[dict[str, Any]] = []

    def objective(parameters: np.ndarray) -> tuple[float, np.ndarray]:
        rows = geometry_function(parameters)
        mol, mf, energy = run_rks(
            rows,
            {
                "basis": settings["basis"],
                "functional": settings["method"],
                "grid_level": settings["grid_level"],
                "scf_tolerance_hartree": settings["scf_tolerance_hartree"],
                "maximum_cycles": 150,
            },
            memory_mb,
        )
        gradient = np.asarray(mf.nuc_grad_method().kernel(), dtype=float)
        if kind == "D2h":
            signs = np.array([
                [-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0],
                [-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0],
            ], dtype=float)
            projected = np.array([
                np.sum(gradient[:4] * signs[:4]) / BOHR_ANGSTROM,
                np.sum(gradient[:4] * signs[:4] * np.array([0, 1, 0])) / BOHR_ANGSTROM,
                np.sum(gradient[4:] * signs[4:] * np.array([1, 0, 0])) / BOHR_ANGSTROM,
                np.sum(gradient[4:] * signs[4:] * np.array([0, 1, 0])) / BOHR_ANGSTROM,
            ])
            projected[0] = np.sum(gradient[:4, 0] * signs[:4, 0]) / BOHR_ANGSTROM
            projected[1] = np.sum(gradient[:4, 1] * signs[:4, 1]) / BOHR_ANGSTROM
        else:
            signs = np.array([
                [-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0],
                [-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0],
            ], dtype=float)
            projected = np.array([
                np.sum(gradient[:4] * signs[:4]) / BOHR_ANGSTROM,
                np.sum(gradient[4:] * signs[4:]) / BOHR_ANGSTROM,
            ])
        evaluations.append({
            "parameters_angstrom": parameters.tolist(),
            "energy_hartree": energy,
            "projected_gradient_hartree_per_angstrom": projected.tolist(),
            "gradient_rms_hartree_per_bohr": float(np.sqrt(np.mean(gradient * gradient))),
        })
        return energy, projected

    result = minimize(
        objective,
        np.asarray(initial, dtype=float),
        method="L-BFGS-B",
        jac=True,
        bounds=[tuple(item) for item in bounds],
        options={"maxiter": int(settings["maximum_iterations"]), "ftol": 1e-12, "gtol": 1e-5, "maxls": 20},
    )
    rows = geometry_function(result.x)
    return {
        "kind": kind,
        "optimizer_success": bool(result.success),
        "optimizer_status": int(result.status),
        "optimizer_message": str(result.message),
        "parameters_angstrom": result.x.tolist(),
        "geometry_atoms_angstrom": rows,
        "energy_hartree": float(result.fun),
        "evaluations": evaluations,
    }


def stability_status(mf: Any) -> dict[str, Any]:
    try:
        returned = mf.stability(internal=True, external=False, return_status=True)
        flags = [item for item in returned if isinstance(item, (bool, np.bool_))]
        return {"checked": True, "internally_stable": bool(flags[0]) if flags else None, "error": None}
    except Exception as exc:
        return {"checked": False, "internally_stable": None, "error": f"{type(exc).__name__}: {exc}"}


def uhf_seed_density(mf: Any, angle_degree: float) -> tuple[np.ndarray, np.ndarray]:
    nocc = mf.mol.nelectron // 2
    occupied = np.array(mf.mo_coeff[:, :nocc], copy=True)
    homo = np.array(mf.mo_coeff[:, nocc - 1], copy=True)
    lumo = np.array(mf.mo_coeff[:, nocc], copy=True)
    theta = math.radians(angle_degree)
    alpha = np.array(occupied, copy=True)
    beta = np.array(occupied, copy=True)
    alpha[:, -1] = math.cos(theta) * homo + math.sin(theta) * lumo
    beta[:, -1] = math.cos(theta) * homo - math.sin(theta) * lumo
    return alpha @ alpha.T, beta @ beta.T


def run_single_reference(rows: list[list[Any]], settings: dict[str, Any], memory_mb: int) -> dict[str, Any]:
    mol, rks, rks_energy = run_rks(rows, settings, memory_mb)
    record: dict[str, Any] = {
        "rks": {"converged": bool(rks.converged), "energy_hartree": rks_energy, "stability": stability_status(rks)},
        "broken_symmetry_singlets": [],
    }
    for angle in settings["broken_symmetry_seed_angles_degree"]:
        uks = dft.UKS(mol)
        uks.xc = settings["functional"]
        uks.grids.level = int(settings["grid_level"])
        uks.conv_tol = float(settings["scf_tolerance_hartree"])
        uks.max_cycle = int(settings["maximum_cycles"])
        try:
            energy = float(uks.kernel(dm0=uhf_seed_density(rks, float(angle))))
            s2, multiplicity = uks.spin_square()
            record["broken_symmetry_singlets"].append({
                "seed_angle_degree": float(angle), "converged": bool(uks.converged),
                "energy_hartree": energy, "s2": float(s2), "multiplicity": float(multiplicity),
            })
        except Exception as exc:
            record["broken_symmetry_singlets"].append({
                "seed_angle_degree": float(angle), "converged": False,
                "error": f"{type(exc).__name__}: {exc}",
            })

    triplet_mol = make_molecule(rows, settings["basis"], 2, memory_mb)
    triplet = dft.UKS(triplet_mol)
    triplet.xc = settings["functional"]
    triplet.grids.level = int(settings["grid_level"])
    triplet.conv_tol = float(settings["scf_tolerance_hartree"])
    triplet.max_cycle = int(settings["maximum_cycles"])
    try:
        triplet_energy = float(triplet.kernel())
        s2, multiplicity = triplet.spin_square()
        record["triplet"] = {
            "converged": bool(triplet.converged), "energy_hartree": triplet_energy,
            "s2": float(s2), "multiplicity": float(multiplicity),
            "singlet_triplet_gap_kcal_mol": (triplet_energy - rks_energy) * HARTREE_TO_KCAL_MOL,
        }
    except Exception as exc:
        record["triplet"] = {"converged": False, "error": f"{type(exc).__name__}: {exc}"}
    return record


def carbon_p_weights(
    mol: gto.Mole,
    mo_coeff: np.ndarray,
    selection_mode: str,
) -> np.ndarray:
    labels = mol.ao_labels(fmt=False)
    # The frozen WP1 contract is a pi-space contract.  For the planar CBD
    # geometries the molecular plane is xy, so only carbon p_z AOs may define
    # the active-space character.  PySCF's tuple labels store the shell in
    # row[2] (for example ``2p``) and the Cartesian component in row[3].
    if selection_mode == "carbon_pz":
        indices = [
            i
            for i, row in enumerate(labels)
            if row[0] < 4 and str(row[2]).lower().endswith("p") and str(row[3]).lower() == "z"
        ]
    elif selection_mode == "carbon_2p_all_components":
        indices = [
            i
            for i, row in enumerate(labels)
            if row[0] < 4 and str(row[2]).lower() == "2p" and str(row[3]).lower() in {"x", "y", "z"}
        ]
    else:
        raise ValueError(f"unsupported active-orbital selection mode: {selection_mode}")
    if not indices:
        raise RuntimeError(f"no AOs found for active-orbital selection mode {selection_mode}")
    overlap = mol.intor_symmetric("int1e_ovlp")
    eigenvalues, eigenvectors = np.linalg.eigh(overlap)
    if float(np.min(eigenvalues)) <= 1e-12:
        raise RuntimeError("AO overlap is singular while building carbon-p character")
    overlap_half = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    orthogonal_ao_coeff = overlap_half @ mo_coeff
    return np.sum(orthogonal_ao_coeff[indices, :] ** 2, axis=0)


def select_active_orbitals(
    mol: gto.Mole,
    mf: Any,
    ncas: int,
    nelecas: int,
    selection_mode: str,
) -> tuple[list[int], np.ndarray]:
    weights = carbon_p_weights(mol, mf.mo_coeff, selection_mode)
    nocc = mol.nelectron // 2
    occupied_needed = nelecas // 2
    virtual_needed = ncas - occupied_needed
    occupied_pool = list(range(nocc))
    virtual_pool = list(range(nocc, mf.mo_coeff.shape[1]))
    occupied = sorted(occupied_pool, key=lambda i: (-float(weights[i]), -i))[:occupied_needed]
    virtual = sorted(virtual_pool, key=lambda i: (-float(weights[i]), i))[:virtual_needed]
    selected = sorted(occupied + virtual)
    if len(selected) != ncas:
        raise RuntimeError(f"active orbital selection returned {len(selected)} rather than {ncas}")
    return selected, weights


def run_casscf(
    rows: list[list[Any]],
    basis: str,
    memory_mb: int,
    ncas: int,
    nelecas: int,
    settings: dict[str, Any],
) -> tuple[dict[str, Any], gto.Mole, np.ndarray, np.ndarray]:
    mol = make_molecule(rows, basis, 0, memory_mb)
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-11
    mf.max_cycle = 150
    rhf_energy = float(mf.kernel())
    if not mf.converged:
        raise RuntimeError("RHF reference did not converge")
    selection_mode = "carbon_pz" if (ncas, nelecas) == (4, 4) else "carbon_2p_all_components"
    selected, weights = select_active_orbitals(mol, mf, ncas, nelecas, selection_mode)
    mc = mcscf.CASSCF(mf, ncas, nelecas)
    mc.conv_tol = float(settings["casscf_convergence_tolerance"])
    mc.max_cycle_macro = int(settings["maximum_macro_cycles"])
    mc.fcisolver.nroots = int(settings["state_average_roots"])
    mc = mcscf.state_average_(mc, tuple(float(x) for x in settings["state_average_weights"]))
    # Rebuild the same pi-space from the current geometry's orthonormal RHF
    # orbitals.  Projecting the entire preceding MO set would mix the
    # core/active/virtual partitions; continuity is therefore tested on the
    # resulting active subspaces rather than enforced by full-MO projection.
    initial_mo = mc.sort_mo([index + 1 for index in selected], mf.mo_coeff)
    initialization = (
        "deterministic carbon-pz-character ranking at the current geometry"
        if selection_mode == "carbon_pz"
        else "deterministic total carbon-2p-character ranking at the current geometry"
    )
    e_tot, e_cas, ci, mo_coeff, mo_energy = mc.kernel(initial_mo)
    converged = bool(mc.converged)
    states = [float(x) for x in np.atleast_1d(mc.e_states)]
    rdms = mc.fcisolver.states_make_rdm1(mc.ci, ncas, mc.nelecas)
    noons = [sorted(np.linalg.eigvalsh(np.asarray(rdm)).tolist(), reverse=True) for rdm in rdms]
    state_s2, state_multiplicity = mc.fcisolver.states_spin_square(mc.ci, ncas, mc.nelecas)
    spins = [
        {"s2": float(s2), "multiplicity": float(multiplicity)}
        for s2, multiplicity in zip(state_s2, state_multiplicity, strict=True)
    ]
    # PySCF does not permit direct NEVPT2 evaluation on a state-average
    # solver.  Following its official example, retain the optimized
    # state-average orbitals, run a separated multi-root CASCI, and apply
    # SC-NEVPT2 to each requested root.
    root_casci = mcscf.CASCI(mf, ncas, nelecas)
    root_casci.fcisolver.nroots = int(settings["state_average_roots"])
    root_casci.kernel(mo_coeff)
    root_energies = [float(x) for x in np.atleast_1d(root_casci.e_tot)]
    nevpt_rows = []
    for root in range(len(root_energies)):
        try:
            correction = float(mrpt.NEVPT(root_casci, root=root, density_fit=False).kernel())
            nevpt_rows.append({
                "root": root,
                "status": "PASS",
                "casci_energy_hartree": root_energies[root],
                "correction_hartree": correction,
                "total_hartree": root_energies[root] + correction,
            })
        except Exception as exc:
            nevpt_rows.append({"root": root, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
    ncore = (mol.nelectron - nelecas) // 2
    active_coeff = np.asarray(mo_coeff[:, ncore:ncore + ncas])
    record = {
        "status": "PASS" if bool(converged) else "NOT_CONVERGED",
        "rhf_energy_hartree": rhf_energy,
        "ncas": ncas, "nelecas": nelecas, "ncore": ncore,
        "selected_mo_indices_zero_based": selected,
        "selected_carbon_p_weights": [float(weights[index]) for index in selected],
        "active_orbital_selection_mode": selection_mode,
        "orbital_initialization": initialization,
        "state_average_energy_hartree": float(e_tot),
        "state_energies_hartree": states,
        "root_noons": noons,
        "root_spin_square": spins,
        "sc_nevpt2": nevpt_rows,
    }
    return record, mol, active_coeff, np.asarray(mo_coeff)


def cross_subspace_singular_values(previous_mol: gto.Mole, previous_coeff: np.ndarray, mol: gto.Mole, coeff: np.ndarray) -> list[float]:
    cross = gto.intor_cross("int1e_ovlp", previous_mol, mol)
    overlap = previous_coeff.T @ cross @ coeff
    return np.linalg.svd(overlap, compute_uv=False).tolist()


def interpolate_rows(left: list[list[Any]], right: list[list[Any]], fraction: float) -> list[list[Any]]:
    result = []
    for a, b in zip(left, right, strict=True):
        result.append([a[0], *[(1.0 - fraction) * float(a[i]) + fraction * float(b[i]) for i in range(1, 4)]])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run authorized Science V0.2 WP1 PySCF ladder")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--stage", choices=("endpoints", "cas4-path", "cas12-endpoints", "all"), default="all")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config["work_package"] != "WP1" or config["target_values_present"] is not False:
        raise SystemExit("invalid or unblinded WP1 execution contract")
    if config["resource_limits"]["concurrency"] != 1:
        raise SystemExit("WP1 concurrency contract must remain one")
    if args.validate_only:
        print(json.dumps({"status": "PASS", "config_sha256": sha256(args.config), "scientific_energy_calculation": False}))
        return 0

    os.environ.setdefault("OMP_NUM_THREADS", str(config["resource_limits"]["threads"]))
    os.environ.setdefault("MKL_NUM_THREADS", str(config["resource_limits"]["threads"]))
    start = time.time()
    result: dict[str, Any] = {
        "schema_version": "1.0", "work_package": "WP1", "claim_id": config["claim_id"],
        "estimand_id": config["estimand_id"], "config_sha256": sha256(args.config),
        "scientific_energy_calculation": True, "stage_requested": args.stage,
        "started_epoch": start, "status": "RUNNING", "failures": [],
    }
    if args.checkpoint.is_file():
        prior = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        if prior.get("config_sha256") == result["config_sha256"]:
            result.update(prior)
            result["status"] = "RUNNING"

    try:
        if args.stage in {"endpoints", "all"} and "optimized_endpoints" not in result:
            endpoints = {}
            for kind in ("D2h", "D4h"):
                endpoints[kind] = optimize_endpoint(
                    kind,
                    config["initial_geometries"][kind]["parameters_angstrom"],
                    config["endpoint_optimization"],
                    int(config["resource_limits"]["memory_mb"]),
                )
                result["optimized_endpoints"] = endpoints
                write_json(args.checkpoint, result)
            result["single_reference"] = {}
            for kind, row in endpoints.items():
                result["single_reference"][kind] = run_single_reference(
                    row["geometry_atoms_angstrom"], config["single_reference"], int(config["resource_limits"]["memory_mb"])
                )
                write_json(args.checkpoint, result)

        endpoints = result.get("optimized_endpoints")
        if not endpoints:
            raise RuntimeError("optimized endpoints are required before multireference stages")

        if args.stage in {"cas4-path", "all"} and "cas4_path" not in result:
            path_rows = []
            previous_mol = None
            previous_active_coeff = None
            for fraction in config["path"]["lambda_values"]:
                rows = interpolate_rows(endpoints["D2h"]["geometry_atoms_angstrom"], endpoints["D4h"]["geometry_atoms_angstrom"], float(fraction))
                record, mol, active_coeff, _ = run_casscf(
                    rows, config["multireference"]["orbital_reference"].split("/")[-1],
                    int(config["resource_limits"]["memory_mb"]), 4, 4, config["multireference"],
                )
                record["lambda"] = float(fraction)
                record["geometry_atoms_angstrom"] = rows
                if previous_mol is not None and previous_active_coeff is not None:
                    record["previous_active_subspace_singular_values"] = cross_subspace_singular_values(
                        previous_mol, previous_active_coeff, mol, active_coeff
                    )
                path_rows.append(record)
                result["cas4_path"] = path_rows
                previous_mol = mol
                previous_active_coeff = active_coeff
                write_json(args.checkpoint, result)

        if args.stage in {"cas12-endpoints", "all"} and "cas12_endpoints" not in result:
            result["cas12_endpoints"] = {}
            for kind in ("D2h", "D4h"):
                try:
                    record, _, _, _ = run_casscf(
                        endpoints[kind]["geometry_atoms_angstrom"], config["multireference"]["orbital_reference"].split("/")[-1],
                        int(config["resource_limits"]["memory_mb"]), 12, 12, config["multireference"],
                    )
                except Exception as exc:
                    record = {"status": "AUDITABLE_FAILURE", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}
                result["cas12_endpoints"][kind] = record
                write_json(args.checkpoint, result)

        result["status"] = "PASS_WITH_RETAINED_FAILURES" if result["failures"] else "PASS"
    except Exception as exc:
        result["status"] = "FAILED_RESTARTABLE"
        result["failures"].append({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    result["finished_epoch"] = time.time()
    result["wall_seconds"] = result["finished_epoch"] - start
    write_json(args.checkpoint, result)
    write_json(args.output, result)
    print(json.dumps({"status": result["status"], "output": str(args.output), "wall_seconds": result["wall_seconds"]}))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
