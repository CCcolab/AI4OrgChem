"""Run the qualified P14 B3LYPG/6-31G(d) five-parameter G/PLG optimizations.

This is the narrowly scoped production calculation requested by the v0.3.0
post-release review.  It does not add molecules, functionals, basis sets, or
training labels.
"""

from __future__ import annotations

import argparse
import gc
import json
import resource
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from run_p14_benzotricyclobutadiene_five_parameter_pilot import (
    atoms_from_vector,
    metrics_from_vector,
    optimize_state,
    optimizer_record,
    vector_from_source,
)
from run_p14_benzotricyclobutadiene_smoke import HARTREE_TO_KCAL_PER_MOL, compact_state, write_json
from run_p14_benzotricyclobutadiene_source_level_fixed_geometry import (
    available_memory_mib,
    conditional_state,
    ordinary_state,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
DEFAULT_CLASSES = ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml"
DEFAULT_CHECKPOINT = ROOT / "runs/reproduction/p14/p14_C12H6_production_optimization_checkpoint_v0.1.json"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_C12H6_production_optimization_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_C12H6_production_optimization.md"


def bounds_from_config(options: dict[str, Any]) -> list[tuple[float, float]]:
    return [
        tuple(float(value) for value in options["bounds_angstrom"][name])
        for name in options["parameter_order"]
    ]


def qualify_termination(record: dict[str, Any], tolerance: float) -> None:
    gradient_ok = float(record["gradient_max_abs_hartree_per_angstrom"]) <= tolerance
    record["termination_reason"] = (
        "gradient_tolerance_satisfied" if gradient_ok else "optimizer_stopped_above_gradient_tolerance"
    )


def render_report(record: dict[str, Any]) -> str:
    g = record["optimized_G_geometry"]["metrics"]
    plg = record["optimized_PLG_geometry"]["metrics"]
    return "\n".join(
        [
            "# P14 C12H6 B3LYPG/6-31G(d)五参数生产优化",
            "",
            f"- 资格门禁：`{record['production_gate_verdict']}`。",
            f"- G：Δr=`{g['delta_r_angstrom']:+.6f} Å`，最大梯度=`{record['G_optimizer']['gradient_max_abs_hartree_per_angstrom']:.8f} Eh/Å`。",
            f"- PLG：Δr=`{plg['delta_r_angstrom']:+.6f} Å`，最大梯度=`{record['PLG_optimizer']['gradient_max_abs_hartree_per_angstrom']:.8f} Eh/Å`。",
            f"- dΔr(GP)=`{record['d_delta_r_GP_angstrom']:+.6f} Å`。",
            f"- 优化端点=`{record['optimized_endpoint_kcal_mol']:+.6f} kcal/mol`。",
            "",
            "该记录只有在全部授权、方法、SCF、电子数、梯度、终止原因和边界检查通过时，才具有P14科学分类资格。",
            "",
        ]
    )


def run(protocol_path: Path, classes_path: Path, checkpoint_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    production = protocol["production_calculation"]
    options = production["geometry_optimizer"]
    if not production["authorized"] or not production["geometry_optimization_authorized"]:
        raise RuntimeError("P14 production geometry optimization is not authorized")
    if options["scientific_classification_allowed"] is not True:
        raise RuntimeError("P14 production record must explicitly allow scientific classification")
    memory_before = available_memory_mib()
    if memory_before < float(production["required_available_memory_mib"]):
        raise MemoryError("P14 production optimization requires at least 13000 MiB available memory")

    source = protocol["source_anchors_B3LYP_6_31G_star"]
    initial_r_ch = float(production["fixed_CH_angstrom"])
    initial_g = vector_from_source(source["G"], initial_r_ch)
    initial_plg = vector_from_source(source["PLG"], initial_r_ch)
    bounds = bounds_from_config(options)

    ordinary_plg_anchor, plg_initial_density = ordinary_state(atoms_from_vector(initial_plg), production)
    if not ordinary_plg_anchor["converged"]:
        raise RuntimeError("P14 ordinary PLG descriptor anchor did not converge")

    base_checkpoint = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "stage": "five_parameter_D3h_B3LYPG_6_31Gd_production",
        "scientific_classification_allowed": True,
    }
    g_result, g_evaluations = optimize_state(
        stage="ordinary_G_production",
        initial=initial_g,
        bounds=bounds,
        state_runner=lambda atoms: ordinary_state(atoms, production)[0],
        options=options,
        checkpoint_path=checkpoint_path,
        prior=base_checkpoint,
    )
    g_parameters = np.asarray(g_result.x, dtype=float)
    g_atoms = atoms_from_vector(g_parameters)
    g_state_raw, _ = ordinary_state(g_atoms, production)
    g_optimizer = optimizer_record(g_result, bounds, g_evaluations)

    gc.collect()
    plg_result, plg_evaluations = optimize_state(
        stage="conditional_PLG_production",
        initial=initial_plg,
        bounds=bounds,
        state_runner=lambda atoms: conditional_state(atoms, production, classes, plg_initial_density),
        options=options,
        checkpoint_path=checkpoint_path,
        prior={**base_checkpoint, "ordinary_G_optimizer": g_optimizer},
    )
    plg_parameters = np.asarray(plg_result.x, dtype=float)
    plg_atoms = atoms_from_vector(plg_parameters)
    plg_state_raw = conditional_state(plg_atoms, production, classes, plg_initial_density)
    plg_optimizer = optimizer_record(plg_result, bounds, plg_evaluations)

    tolerance = float(options["gradient_tolerance_hartree_per_angstrom"])
    qualify_termination(g_optimizer, tolerance)
    qualify_termination(plg_optimizer, tolerance)
    expected = float(options["acceptance"]["electron_count"])
    electron_tolerance = float(options["acceptance"]["electron_count_tolerance"])
    peak_rss_mib = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    checks = {
        "scientific_classification_allowed": True,
        "production_optimization_authorized": True,
        "method_is_B3LYPG": str(production["pyscf_xc"]).upper() == "B3LYPG",
        "basis_is_6_31Gd": str(production["basis"]).lower() == "6-31g(d)",
        "G_optimizer_success": bool(g_optimizer["success"]),
        "G_gradient_within_tolerance": float(g_optimizer["gradient_max_abs_hartree_per_angstrom"]) <= tolerance,
        "G_no_active_bound": not g_optimizer["active_bounds"],
        "G_state_converged": bool(g_state_raw["converged"]),
        "G_78_electrons": abs(float(g_state_raw["physical_metric_electron_count"]) - expected) <= electron_tolerance,
        "PLG_optimizer_success": bool(plg_optimizer["success"]),
        "PLG_gradient_within_tolerance": float(plg_optimizer["gradient_max_abs_hartree_per_angstrom"]) <= tolerance,
        "PLG_no_active_bound": not plg_optimizer["active_bounds"],
        "PLG_state_converged": bool(plg_state_raw["converged"]),
        "PLG_78_electrons": abs(float(plg_state_raw["physical_metric_electron_count"]) - expected) <= electron_tolerance,
        "PLG_energy_components_close": float(plg_state_raw["energy_component_closure_residual_hartree"]) <= 1.0e-9,
        "PLG_commutator_closed": float(plg_state_raw["final_commutator_frobenius_norm"]) <= 1.0e-5,
        "PLG_density_idempotent": float(plg_state_raw["closed_shell_idempotency_relative_residual"]) <= 1.0e-7,
        "memory_within_limit": peak_rss_mib <= float(options["acceptance"]["maximum_peak_rss_mib"]),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    g_metrics = metrics_from_vector(g_parameters)
    plg_metrics = metrics_from_vector(plg_parameters)
    record = {
        **base_checkpoint,
        "method": {
            "engine": "PySCF_plus_SciPy",
            "pyscf_xc": production["pyscf_xc"],
            "basis": production["basis"],
            "grid_level": production["grid_level"],
            "parameter_order": options["parameter_order"],
            "original_program_code_used": False,
            "fit_to_published_values": False,
        },
        "optimized_G_geometry": {"parameters_angstrom": g_parameters.tolist(), "atoms_angstrom": g_atoms, "metrics": g_metrics},
        "G_state": g_state_raw,
        "G_optimizer": g_optimizer,
        "optimized_PLG_geometry": {"parameters_angstrom": plg_parameters.tolist(), "atoms_angstrom": plg_atoms, "metrics": plg_metrics},
        "PLG_state": compact_state(plg_state_raw),
        "PLG_optimizer": plg_optimizer,
        "d_delta_r_GP_angstrom": float(g_metrics["delta_r_angstrom"] - plg_metrics["delta_r_angstrom"]),
        "optimized_endpoint_kcal_mol": (float(g_state_raw["total_energy_hartree"]) - float(plg_state_raw["total_energy_hartree"])) * HARTREE_TO_KCAL_PER_MOL,
        "acceptance_checks": checks,
        "pilot_gate_verdict": "PASS" if all(checks.values()) else "FAIL",
        "production_gate_verdict": "PASS" if all(checks.values()) else "FAIL",
        "memory_before_mib": memory_before,
        "peak_rss_mib": peak_rss_mib,
        "wall_time_seconds": time.perf_counter() - started,
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
    args = parser.parse_args()
    record = run(args.protocol, args.classes, args.checkpoint)
    write_json(args.output, record)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(record), encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": record["production_gate_verdict"], "output": str(args.output), "wall_time_seconds": record["wall_time_seconds"]}, ensure_ascii=False), flush=True)
    return 0 if record["production_gate_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
