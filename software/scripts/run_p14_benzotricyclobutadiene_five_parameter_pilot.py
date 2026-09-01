"""Optimize the frozen P14 C12H6 G/PLG states in a five-parameter D3h model.

This STO-3G pilot validates the geometry-optimization path only.  It cannot
produce the final P14 scientific classification or a training label.
"""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import yaml

from ai4orgchem.qm.p09_ao_classification import classify_planar_pyscf_aos
from ai4orgchem.qm.p09_conditional_scf import run_p09_conditional_rks
from run_p14_benzotricyclobutadiene_smoke import (
    HARTREE_TO_KCAL_PER_MOL,
    build_mean_field,
    build_molecule,
    compact_state,
    d3h_atoms,
    geometry_metrics,
    write_json,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
DEFAULT_CLASSES = ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml"
DEFAULT_CHECKPOINT = ROOT / "runs/reproduction/p14/p14_C12H6_five_parameter_pilot_checkpoint_v0.1.json"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_C12H6_five_parameter_pilot_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_C12H6_five_parameter_pilot.md"


def vector_from_source(source: dict[str, Any], r_ch: float) -> np.ndarray:
    return np.asarray(
        [
            source["rendo_angstrom"],
            source["rexo_angstrom"],
            source["rside_angstrom"],
            source["router_angstrom"],
            r_ch,
        ],
        dtype=float,
    )


def atoms_from_vector(parameters: np.ndarray) -> list[list[Any]]:
    values = np.asarray(parameters, dtype=float)
    return d3h_atoms(
        {
            "rendo_angstrom": float(values[0]),
            "rexo_angstrom": float(values[1]),
            "rside_angstrom": float(values[2]),
            "router_angstrom": float(values[3]),
        },
        float(values[4]),
    )


def metrics_from_vector(parameters: np.ndarray) -> dict[str, float]:
    values = np.asarray(parameters, dtype=float)
    result = geometry_metrics(atoms_from_vector(values))
    result["rCH_angstrom"] = float(values[4])
    return result


def ordinary_state(atoms: list[list[Any]], protocol: dict[str, Any]) -> dict[str, Any]:
    molecule = build_molecule(atoms, protocol)
    mean_field = build_mean_field(molecule, protocol)
    energy = float(mean_field.kernel())
    density = np.asarray(mean_field.make_rdm1(), dtype=float)
    overlap = np.asarray(mean_field.get_ovlp(), dtype=float)
    return {
        "converged": bool(mean_field.converged),
        "total_energy_hartree": energy,
        "electronic_energy_hartree": energy - float(molecule.energy_nuc()),
        "nuclear_repulsion_hartree": float(molecule.energy_nuc()),
        "physical_metric_electron_count": float(np.einsum("pq,qp->", overlap, density)),
        "density": density,
    }


def conditional_state(
    atoms: list[list[Any]],
    protocol: dict[str, Any],
    classes: dict[str, Any],
    initial_density: np.ndarray,
) -> dict[str, Any]:
    molecule = build_molecule(atoms, protocol)
    mean_field = build_mean_field(molecule, protocol)
    fragment_map = {index: "A" if index < 6 else "B" for index in range(12)}
    descriptors = classify_planar_pyscf_aos(molecule, fragment_map)
    options = protocol["smoke_gate"]["conditional_scf"]
    return run_p09_conditional_rks(
        mean_field,
        descriptors,
        classes["exchange_integral_classes"],
        initial_density=initial_density,
        maximum_cycles=int(options["maximum_cycles"]),
        density_tolerance=float(options["density_tolerance"]),
        energy_tolerance=float(options["energy_tolerance_hartree"]),
        diis_start_cycle=int(options["diis_start_cycle"]),
        diis_space=int(options["diis_space"]),
        damping_cycles=int(options["damping_cycles"]),
        damping=float(options["damping"]),
    )


def optimizer_bounds(pilot: dict[str, Any]) -> list[tuple[float, float]]:
    return [
        tuple(float(value) for value in pilot["bounds_angstrom"][name])
        for name in pilot["parameter_order"]
    ]


def optimize_state(
    *,
    stage: str,
    initial: np.ndarray,
    bounds: list[tuple[float, float]],
    state_runner: Callable[[list[list[Any]]], dict[str, Any]],
    options: dict[str, Any],
    checkpoint_path: Path,
    prior: dict[str, Any],
) -> tuple[Any, list[dict[str, Any]]]:
    from scipy.optimize import minimize

    evaluations: list[dict[str, Any]] = []
    cache: dict[tuple[float, ...], float] = {}

    def objective(parameters: np.ndarray) -> float:
        key = tuple(float(value) for value in np.round(parameters, decimals=12))
        if key in cache:
            return cache[key]
        state = state_runner(atoms_from_vector(parameters))
        if not state["converged"]:
            raise RuntimeError(f"P14 {stage} SCF failed during five-parameter pilot")
        electron_count = float(
            state.get("masked_metric_electron_count", state["physical_metric_electron_count"])
        )
        row = {
            "evaluation": len(evaluations) + 1,
            "parameters_angstrom": [float(value) for value in parameters],
            "delta_r_angstrom": float(parameters[0] - parameters[1]),
            "energy_hartree": float(state["total_energy_hartree"]),
            "scf_cycles": int(state.get("cycles", 0)),
            "metric_electron_count": electron_count,
        }
        evaluations.append(row)
        cache[key] = row["energy_hartree"]
        write_json(
            checkpoint_path,
            {
                **prior,
                "stage": f"P14_{stage}_five_parameter_optimization_in_progress",
                "current_initial_parameters_angstrom": initial.tolist(),
                "current_bounds_angstrom": bounds,
                f"{stage}_evaluations": evaluations,
            },
        )
        print(json.dumps({"stage": stage, **row}, ensure_ascii=False), flush=True)
        return row["energy_hartree"]

    result = minimize(
        objective,
        initial,
        method=str(options["method"]),
        jac=str(options["finite_difference_scheme"]),
        bounds=bounds,
        options={
            "maxiter": int(options["maximum_iterations"]),
            "maxfun": int(options["maximum_function_evaluations"]),
            "ftol": float(options["function_tolerance"]),
            "gtol": float(options["gradient_tolerance_hartree_per_angstrom"]),
            "maxls": int(options["maximum_line_search_steps"]),
            "finite_diff_rel_step": float(options["finite_difference_relative_step"]),
        },
    )
    return result, evaluations


def optimizer_record(
    result: Any,
    bounds: list[tuple[float, float]],
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    parameters = np.asarray(result.x, dtype=float)
    gradient = np.asarray(result.jac, dtype=float)
    active_bounds = [
        index
        for index, (value, interval) in enumerate(zip(parameters, bounds, strict=True))
        if abs(float(value) - interval[0]) <= 1.0e-6
        or abs(float(value) - interval[1]) <= 1.0e-6
    ]
    return {
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "iterations": int(result.nit),
        "function_evaluations": int(result.nfev),
        "gradient_hartree_per_angstrom": gradient.tolist(),
        "gradient_max_abs_hartree_per_angstrom": float(np.max(np.abs(gradient))),
        "active_bounds": active_bounds,
        "bounds_angstrom": bounds,
        "evaluations": evaluations,
    }


def render_report(record: dict[str, Any]) -> str:
    g = record["optimized_G_geometry"]["metrics"]
    plg = record["optimized_PLG_geometry"]["metrics"]
    return "\n".join(
        [
            "# P14 C12H6五参数D3h优化技术试算",
            "",
            f"- 协议：`{record['protocol_id']}`。",
            "- 层级：B3LYPG/STO-3G；仅验证普通G/条件PLG几何优化路径。",
            f"- 普通G：Δr = `{g['delta_r_angstrom']:+.6f} Å`，E = `{record['G_state']['total_energy_hartree']:+.12f} Eh`。",
            f"- 条件PLG：Δr = `{plg['delta_r_angstrom']:+.6f} Å`，E = `{record['PLG_state']['total_energy_hartree']:+.12f} Eh`。",
            f"- dΔr(GP) = `{record['d_delta_r_GP_angstrom']:+.6f} Å`。",
            f"- 技术端点 = `{record['technical_endpoint_kcal_mol']:+.6f} kcal/mol`。",
            f"- 门禁：`{record['pilot_gate_verdict']}`。",
            "",
            "该试算不替代B3LYP/6-31G*生产计算，不生成P14科学分类或AI训练标签。",
            "",
        ]
    )


def run(protocol_path: Path, classes_path: Path, checkpoint_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    pilot = protocol["five_parameter_pilot"]
    if not pilot["authorized"] or pilot["scientific_classification_allowed"]:
        raise RuntimeError("P14 five-parameter technical pilot authorization is invalid")

    source = protocol["source_anchors_B3LYP_6_31G_star"]
    initial_r_ch = float(pilot["initial_rCH_angstrom"])
    initial_g = vector_from_source(source["G"], initial_r_ch)
    initial_plg = vector_from_source(source["PLG"], initial_r_ch)
    bounds = optimizer_bounds(pilot)
    options = pilot["optimizer"]

    ordinary_plg_anchor = ordinary_state(atoms_from_vector(initial_plg), protocol)
    if not ordinary_plg_anchor["converged"]:
        raise RuntimeError("P14 ordinary PLG descriptor anchor did not converge")
    plg_initial_density = np.asarray(ordinary_plg_anchor["density"], dtype=float)

    base_checkpoint = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "scientific_classification_allowed": False,
    }
    g_result, g_evaluations = optimize_state(
        stage="ordinary_G",
        initial=initial_g,
        bounds=bounds,
        state_runner=lambda atoms: ordinary_state(atoms, protocol),
        options=options,
        checkpoint_path=checkpoint_path,
        prior=base_checkpoint,
    )
    g_parameters = np.asarray(g_result.x, dtype=float)
    g_atoms = atoms_from_vector(g_parameters)
    g_state_raw = ordinary_state(g_atoms, protocol)
    g_optimizer = optimizer_record(g_result, bounds, g_evaluations)

    plg_result, plg_evaluations = optimize_state(
        stage="conditional_PLG",
        initial=initial_plg,
        bounds=bounds,
        state_runner=lambda atoms: conditional_state(
            atoms, protocol, classes, plg_initial_density
        ),
        options=options,
        checkpoint_path=checkpoint_path,
        prior={**base_checkpoint, "ordinary_G_optimizer": g_optimizer},
    )
    plg_parameters = np.asarray(plg_result.x, dtype=float)
    plg_atoms = atoms_from_vector(plg_parameters)
    plg_state_raw = conditional_state(
        plg_atoms, protocol, classes, plg_initial_density
    )
    plg_optimizer = optimizer_record(plg_result, bounds, plg_evaluations)

    g_metrics = metrics_from_vector(g_parameters)
    plg_metrics = metrics_from_vector(plg_parameters)
    technical_endpoint = (
        float(g_state_raw["total_energy_hartree"])
        - float(plg_state_raw["total_energy_hartree"])
    ) * HARTREE_TO_KCAL_PER_MOL
    acceptance = pilot["acceptance"]
    expected_electrons = float(acceptance["electron_count"])
    electron_tolerance = float(acceptance["electron_count_tolerance"])
    checks = {
        "G_optimizer_success": bool(g_optimizer["success"]),
        "G_no_active_bound": len(g_optimizer["active_bounds"]) == 0,
        "G_state_converged": bool(g_state_raw["converged"]),
        "G_78_electrons": abs(float(g_state_raw["physical_metric_electron_count"]) - expected_electrons) <= electron_tolerance,
        "PLG_optimizer_success": bool(plg_optimizer["success"]),
        "PLG_no_active_bound": len(plg_optimizer["active_bounds"]) == 0,
        "PLG_state_converged": bool(plg_state_raw["converged"]),
        "PLG_78_electrons": abs(float(plg_state_raw["masked_metric_electron_count"]) - expected_electrons) <= electron_tolerance,
        "PLG_energy_components_close": float(plg_state_raw["energy_component_closure_residual_hartree"]) <= float(acceptance["energy_component_closure_hartree"]),
        "PLG_commutator_closed": float(plg_state_raw["final_commutator_frobenius_norm"]) <= float(acceptance["commutator_frobenius_tolerance"]),
        "PLG_density_idempotent": float(plg_state_raw["closed_shell_idempotency_relative_residual"]) <= float(acceptance["idempotency_relative_tolerance"]),
        "scientific_classification_disabled": pilot["scientific_classification_allowed"] is False,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    peak_rss_mib = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    checks["memory_within_pilot_limit"] = peak_rss_mib <= float(acceptance["maximum_peak_rss_mib"])
    record = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "stage": "five_parameter_D3h_STO3G_technical_pilot",
        "scientific_classification_allowed": False,
        "method": {
            "engine": "PySCF_plus_SciPy",
            "pyscf_xc": pilot["pyscf_xc"],
            "basis": pilot["basis"],
            "parameter_order": pilot["parameter_order"],
            "original_program_code_used": False,
            "fit_to_published_values": False,
        },
        "optimized_G_geometry": {
            "parameters_angstrom": g_parameters.tolist(),
            "atoms_angstrom": g_atoms,
            "metrics": g_metrics,
        },
        "G_state": compact_state(g_state_raw),
        "G_optimizer": g_optimizer,
        "optimized_PLG_geometry": {
            "parameters_angstrom": plg_parameters.tolist(),
            "atoms_angstrom": plg_atoms,
            "metrics": plg_metrics,
        },
        "PLG_state": compact_state(plg_state_raw),
        "PLG_optimizer": plg_optimizer,
        "d_delta_r_GP_angstrom": float(g_metrics["delta_r_angstrom"] - plg_metrics["delta_r_angstrom"]),
        "technical_endpoint_kcal_mol": technical_endpoint,
        "acceptance_checks": checks,
        "pilot_gate_verdict": "PASS" if all(checks.values()) else "FAIL",
        "wall_time_seconds": time.perf_counter() - started,
        "peak_rss_mib": peak_rss_mib,
        "thread_count": 8,
        "production_label": False,
        "training_eligible": False,
    }
    write_json(checkpoint_path, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    record = run(arguments.protocol, arguments.classes, arguments.checkpoint)
    write_json(arguments.output, record)
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(render_report(record), encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": record["pilot_gate_verdict"],
                "G_delta_r_angstrom": record["optimized_G_geometry"]["metrics"]["delta_r_angstrom"],
                "PLG_delta_r_angstrom": record["optimized_PLG_geometry"]["metrics"]["delta_r_angstrom"],
                "d_delta_r_GP_angstrom": record["d_delta_r_GP_angstrom"],
                "technical_endpoint_kcal_mol": record["technical_endpoint_kcal_mol"],
                "wall_time_seconds": record["wall_time_seconds"],
                "peak_rss_mib": record["peak_rss_mib"],
                "output": str(arguments.output),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0 if record["pilot_gate_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
