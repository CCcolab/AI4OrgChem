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
import yaml
from pyscf import dft, gto

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai4orgchem.qm.p09_ao_classification import classify_planar_pyscf_aos
from ai4orgchem.qm.p09_conditional_scf import run_p09_conditional_rks


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def molecule(rows: list[list[Any]], settings: dict[str, Any], memory_mb: int, verbose: int = 0) -> gto.Mole:
    return gto.M(
        atom=[(row[0], tuple(float(x) for x in row[1:4])) for row in rows],
        basis=settings["basis"], charge=0, spin=0, unit="Angstrom",
        symmetry=False, verbose=verbose, max_memory=memory_mb,
    )


def ordinary_rks(rows: list[list[Any]], settings: dict[str, Any], memory_mb: int):
    mol = molecule(rows, settings, memory_mb)
    mf = dft.RKS(mol)
    mf.xc = settings["functional"]
    mf.grids.level = int(settings["grid_level"])
    mf.conv_tol = float(settings["scf_tolerance_hartree"])
    mf.max_cycle = int(settings["maximum_cycles"])
    total = float(mf.kernel())
    if not mf.converged:
        mf = mf.newton()
        mf.conv_tol = float(settings["scf_tolerance_hartree"])
        mf.max_cycle = int(settings["maximum_cycles"])
        total = float(mf.kernel(mo_coeff=mf.mo_coeff, mo_occ=mf.mo_occ))
    nuclear = float(mol.energy_nuc())
    return mol, mf, {
        "converged": bool(mf.converged),
        "total_energy_hartree": total,
        "electronic_energy_hartree": total - nuclear,
        "nuclear_repulsion_hartree": nuclear,
    }


def displaced_geometry(
    reference: list[list[Any]],
    vector: list[list[float]],
    amplitude: float,
    masses: np.ndarray,
) -> list[list[Any]]:
    xyz = np.asarray([row[1:4] for row in reference], dtype=float)
    direction = np.asarray(vector, dtype=float)
    max_norm = float(np.max(np.linalg.norm(direction, axis=1)))
    if max_norm <= 0.0:
        raise ValueError("zero WP3 displacement vector")
    moved = xyz + float(amplitude) * direction / max_norm
    center = np.average(moved, axis=0, weights=masses)
    reference_center = np.average(xyz, axis=0, weights=masses)
    moved += reference_center - center
    moved[:, 2] = xyz[:, 2]
    return [[reference[i][0], *moved[i].tolist()] for i in range(len(reference))]


def compact_conditional(value: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "converged", "cycles", "total_energy_hartree", "electronic_energy_hartree",
        "nuclear_repulsion_hartree", "energy_component_closure_residual_hartree",
        "grid_electron_count", "masked_metric_electron_count", "physical_metric_electron_count",
        "masked_overlap_minimum_eigenvalue", "masked_overlap_condition_number",
        "masked_overlap_cross_pi_max_abs", "conditional_fock_cross_pi_max_abs",
        "deleted_eri_count", "total_eri_count", "deleted_eri_fraction", "eri_storage_mode",
        "final_commutator_frobenius_norm", "closed_shell_idempotency_relative_residual",
        "occupied_virtual_gap_hartree",
    )
    return {key: value[key] for key in keys if key in value}


def curvature(points: list[dict[str, Any]], key: str, fit_window: float) -> float:
    selected = [row for row in points if abs(float(row["amplitude_angstrom"])) <= fit_window + 1e-15]
    x = np.square(np.asarray([row["amplitude_angstrom"] for row in selected], dtype=float))
    y = np.asarray([row[key] for row in selected], dtype=float)
    return 2.0 * float(np.polyfit(x, y, 1)[0])


def analyze_hessian(
    raw_hessian: np.ndarray,
    rows: list[list[Any]],
    seed_record: dict[str, Any],
) -> dict[str, Any]:
    natm = len(rows)
    matrix = np.asarray(raw_hessian).transpose(0, 2, 1, 3).reshape(3 * natm, 3 * natm)
    masses = np.asarray([seed_record["atomic_masses_u"][row[0]] for row in rows], dtype=float)
    scale = np.repeat(np.sqrt(masses), 3)
    mass_weighted = matrix / scale[:, None] / scale[None, :]
    eigenvalues, eigenvectors = np.linalg.eigh(mass_weighted)
    modes = {row["mode_id"]: np.asarray(row["mass_weighted_vector"], dtype=float).reshape(-1) for row in seed_record["modes"]}

    comparisons: dict[str, Any] = {}
    for mode_id in ("B2u_BLA", "A1g_breathing"):
        overlaps = np.abs(eigenvectors.T @ modes[mode_id])
        index = int(np.argmax(overlaps))
        comparisons[mode_id] = {
            "best_eigenmode_index": index,
            "absolute_overlap": float(overlaps[index]),
            "eigenvalue_hartree_per_bohr2_per_amu": float(eigenvalues[index]),
        }

    seed_subspace = np.column_stack([modes["E2g_bend_cos"], modes["E2g_bend_sin"]])
    projections = np.sum((eigenvectors.T @ seed_subspace) ** 2, axis=1)
    indices = np.argsort(projections)[-2:]
    overlap = seed_subspace.T @ eigenvectors[:, indices]
    singular_values = np.linalg.svd(overlap, compute_uv=False)
    ranked = [int(i) for i in np.argsort(projections)[::-1]]
    mixed_indices: list[int] = []
    mixed_singular_values = np.zeros(2)
    threshold = float(seed_record["hessian_comparison_rule_for_gate_v2_3"]["minimum_accepted_overlap_or_singular_value"])
    for index in ranked:
        mixed_indices.append(index)
        mixed_overlap = seed_subspace.T @ eigenvectors[:, mixed_indices]
        mixed_singular_values = np.linalg.svd(mixed_overlap, compute_uv=False)
        if len(mixed_indices) >= 2 and float(np.min(mixed_singular_values)) >= threshold:
            break
    comparisons["E2g"] = {
        "best_eigenmode_indices": [int(i) for i in indices],
        "principal_singular_values": singular_values.tolist(),
        "eigenvalues_hartree_per_bohr2_per_amu": [float(eigenvalues[i]) for i in indices],
        "minimum_mixed_eigensubspace_indices": mixed_indices,
        "mixed_eigensubspace_principal_singular_values": mixed_singular_values.tolist(),
        "mixed_eigensubspace_eigenvalues_hartree_per_bohr2_per_amu": [float(eigenvalues[i]) for i in mixed_indices],
        "mode_mixing_detected": len(mixed_indices) > 2,
    }
    return {
        "eigenvalues_hartree_per_bohr2_per_amu": eigenvalues.tolist(),
        "comparisons": comparisons,
        "minimum_required_overlap": threshold,
        "one_dimensional_modes_pass": all(comparisons[x]["absolute_overlap"] >= threshold for x in ("B2u_BLA", "A1g_breathing")),
        "e2g_subspace_pass": bool(float(np.min(singular_values)) >= threshold),
        "e2g_mixed_subspace_pass": bool(float(np.min(mixed_singular_values)) >= threshold),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run authorized Science V0.2 WP3 benzene mechanism calculation")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--stage", choices=("hessian", "grid", "all"), default="all")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config["work_package"] != "WP3" or config["target_values_present"] is not False:
        raise SystemExit("invalid or unblinded WP3 contract")
    if config["resource_limits"]["concurrency"] != 1:
        raise SystemExit("WP3 concurrency must be one")
    if args.validate_only:
        print(json.dumps({"status": "PASS", "scientific_energy_calculation": False, "config_sha256": sha256(args.config)}))
        return 0

    geometry_path = Path(config["geometry"]["source"])
    seed_path = Path(config["mode_seed"]["source"])
    classes_path = Path(config["conditional_state"]["exchange_classes"])
    if sha256(geometry_path).lower() != config["geometry"]["source_sha256"].lower():
        raise SystemExit("WP3 geometry source hash mismatch")
    geometry_record = json.loads(geometry_path.read_text(encoding="utf-8"))
    seeds = json.loads(seed_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    rows = geometry_record["optimized_G_geometry"]["atoms_angstrom"]
    masses = np.asarray([seeds["atomic_masses_u"][row[0]] for row in rows], dtype=float)

    result: dict[str, Any] = {
        "schema_version": "1.0", "work_package": "WP3", "claim_id": config["claim_id"],
        "estimand_id": config["estimand_id"], "config_sha256": sha256(args.config),
        "geometry_source_sha256": sha256(geometry_path), "mode_seed_sha256": sha256(seed_path),
        "scientific_energy_calculation": True, "status": "RUNNING", "failures": [],
    }
    if args.checkpoint.is_file():
        prior = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        if prior.get("config_sha256") == result["config_sha256"]:
            result.update(prior)
            result["status"] = "RUNNING"
    started = time.time()
    try:
        if args.stage in {"hessian", "all"} and "hessian" not in result:
            mol, mf, ordinary = ordinary_rks(rows, config["ordinary_state"], int(config["resource_limits"]["memory_mb"]))
            raw_hessian = np.asarray(mf.Hessian().kernel(), dtype=float)
            result["reference_ordinary_state"] = ordinary
            result["hessian"] = analyze_hessian(raw_hessian, rows, seeds)
            write_json(args.checkpoint, result)

        if args.stage in {"grid", "all"} and "displacement_modes" not in result:
            mode_map = {row["mode_id"]: row for row in seeds["modes"]}
            fragment_map = {int(key): value for key, value in config["conditional_state"]["fragment_map"].items()}
            result["displacement_modes"] = {}
            for mode_id in config["displacement"]["modes"]:
                mode_rows = []
                for amplitude in config["displacement"]["signed_max_cartesian_displacement_angstrom"]:
                    moved = displaced_geometry(rows, mode_map[mode_id]["cartesian_displacement_per_unit_Q"], float(amplitude), masses)
                    mol, mf, ordinary = ordinary_rks(moved, config["ordinary_state"], int(config["resource_limits"]["memory_mb"]))
                    point: dict[str, Any] = {"amplitude_angstrom": float(amplitude), "ordinary": ordinary}
                    try:
                        descriptors = classify_planar_pyscf_aos(mol, fragment_map)
                        conditional = run_p09_conditional_rks(
                            mf, descriptors, classes["exchange_integral_classes"],
                            initial_density=np.asarray(mf.make_rdm1(), dtype=float),
                            maximum_cycles=int(config["conditional_state"]["maximum_cycles"]),
                            density_tolerance=float(config["conditional_state"]["density_tolerance"]),
                            energy_tolerance=float(config["conditional_state"]["energy_tolerance_hartree"]),
                            memory_controlled_eri=bool(config["conditional_state"]["memory_controlled_eri"]),
                        )
                        point["conditional"] = compact_conditional(conditional)
                    except Exception as exc:
                        point["conditional"] = {"converged": False, "error": f"{type(exc).__name__}: {exc}"}
                    mode_rows.append(point)
                    result["displacement_modes"][mode_id] = {"points": mode_rows}
                    write_json(args.checkpoint, result)

                fit_window = max(abs(float(x)) for x in config["displacement"]["primary_fit_window_angstrom"])
                # Dotted paths are expanded explicitly to keep the fitting helper simple.
                flattened = []
                for point in mode_rows:
                    flattened.append({
                        "amplitude_angstrom": point["amplitude_angstrom"],
                        "ordinary_total": point["ordinary"]["total_energy_hartree"],
                        "ordinary_electronic": point["ordinary"]["electronic_energy_hartree"],
                        "ordinary_nuclear": point["ordinary"]["nuclear_repulsion_hartree"],
                        "conditional_electronic": point["conditional"].get("electronic_energy_hartree"),
                    })
                def fit(key: str) -> float:
                    return curvature(flattened, key, fit_window)
                ordinary_curvatures = {"total": fit("ordinary_total"), "electronic": fit("ordinary_electronic"), "nuclear": fit("ordinary_nuclear")}
                conditional_ok = all(row["conditional_electronic"] is not None for row in flattened)
                conditional_electronic = fit("conditional_electronic") if conditional_ok else None
                result["displacement_modes"][mode_id]["curvatures_hartree_per_angstrom2"] = {
                    "ordinary": ordinary_curvatures,
                    "conditional_electronic": conditional_electronic,
                    "delta_k_e_conditional_minus_ordinary": (
                        conditional_electronic - ordinary_curvatures["electronic"] if conditional_electronic is not None else None
                    ),
                    "ordinary_closure_residual": ordinary_curvatures["total"] - ordinary_curvatures["electronic"] - ordinary_curvatures["nuclear"],
                }
                write_json(args.checkpoint, result)

        result["status"] = "PASS_WITH_RETAINED_FAILURES" if result["failures"] else "PASS"
    except Exception as exc:
        result["status"] = "FAILED_RESTARTABLE"
        result["failures"].append({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    result["wall_seconds_this_run"] = time.time() - started
    write_json(args.checkpoint, result)
    write_json(args.output, result)
    print(json.dumps({"status": result["status"], "output": str(args.output), "wall_seconds": result["wall_seconds_this_run"]}))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
