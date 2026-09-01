"""Run the P14 source-level B3LYPG/6-31G(d) fixed-geometry anchor gate."""

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

from ai4orgchem.qm.p09_ao_classification import classify_planar_pyscf_aos
from ai4orgchem.qm.p09_conditional_scf import run_p09_conditional_rks
from run_p14_benzotricyclobutadiene_smoke import (
    HARTREE_TO_KCAL_PER_MOL,
    compact_state,
    d3h_atoms,
    geometry_metrics,
    write_json,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
DEFAULT_CLASSES = ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml"
DEFAULT_CHECKPOINT = ROOT / "runs/reproduction/p14/p14_C12H6_source_level_fixed_geometry_checkpoint_v0.1.json"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_C12H6_source_level_fixed_geometry_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_C12H6_source_level_fixed_geometry.md"


def available_memory_mib() -> float:
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemAvailable:"):
            return float(line.split()[1]) / 1024.0
    raise RuntimeError("MemAvailable is unavailable")


def build_molecule(atoms: list[list[Any]], production: dict[str, Any]) -> Any:
    from pyscf import gto

    return gto.M(
        atom=atoms,
        basis=str(production["basis"]),
        charge=0,
        spin=0,
        unit="Angstrom",
        symmetry=False,
        verbose=0,
    )


def build_mean_field(molecule: Any, production: dict[str, Any]) -> Any:
    from pyscf import dft

    mean_field = dft.RKS(molecule)
    mean_field.verbose = 0
    mean_field.xc = str(production["pyscf_xc"])
    mean_field.grids.level = int(production["grid_level"])
    mean_field.conv_tol = float(production["scf_tolerance_hartree"])
    mean_field.max_cycle = int(production["maximum_scf_cycles"])
    mean_field.max_memory = int(production["numerical_integration_memory_mb"])
    return mean_field


def ordinary_state(
    atoms: list[list[Any]], production: dict[str, Any]
) -> tuple[dict[str, Any], np.ndarray]:
    molecule = build_molecule(atoms, production)
    mean_field = build_mean_field(molecule, production)
    energy = float(mean_field.kernel())
    density = np.asarray(mean_field.make_rdm1(), dtype=float)
    overlap = np.asarray(mean_field.get_ovlp(), dtype=float)
    record = {
        "converged": bool(mean_field.converged),
        "total_energy_hartree": energy,
        "electronic_energy_hartree": energy - float(molecule.energy_nuc()),
        "nuclear_repulsion_hartree": float(molecule.energy_nuc()),
        "physical_metric_electron_count": float(np.einsum("pq,qp->", overlap, density)),
        "nao": int(molecule.nao_nr()),
    }
    del mean_field, molecule, overlap
    gc.collect()
    return record, density


def conditional_state(
    atoms: list[list[Any]],
    production: dict[str, Any],
    classes: dict[str, Any],
    initial_density: np.ndarray,
) -> dict[str, Any]:
    molecule = build_molecule(atoms, production)
    mean_field = build_mean_field(molecule, production)
    descriptors = classify_planar_pyscf_aos(
        molecule, {index: "A" if index < 6 else "B" for index in range(12)}
    )
    options = production["conditional_scf"]
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
        memory_controlled_eri=bool(options["memory_controlled_eri"]),
    )


def render_report(record: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# P14 C12H6原著层级固定几何锚点",
            "",
            "- 方法：B3LYPG/6-31G(d)，source-G/source-PLG描述符重构，C-H固定为1.080 Å。",
            f"- ordinary@G：`{record['ordinary_G']['total_energy_hartree']:+.10f} Eh`；原著 `{record['source_comparison']['G_source_energy_hartree']:+.10f} Eh`。",
            f"- conditional-PLG@PLG：`{record['conditional_PLG']['total_energy_hartree']:+.10f} Eh`；原著 `{record['source_comparison']['PLG_source_energy_hartree']:+.10f} Eh`。",
            f"- 固定几何端点：`{record['fixed_geometry_endpoint_kcal_mol']:+.6f} kcal/mol`；原著优化端点 `{record['source_comparison']['source_delta_E_GP_kcal_mol']:+.6f} kcal/mol`。",
            f"- 门禁：`{record['anchor_gate_verdict']}`。",
            "",
            "该门禁只判断原著层级固定几何能量与算符可运行性；由于C-H为代理值且几何未独立优化，不单独发布最终P14分类。",
            "",
        ]
    )


def run(
    protocol_path: Path,
    classes_path: Path,
    checkpoint_path: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    production = protocol["production_calculation"]
    if not production["authorized"] or production["current_scope"] != "fixed_source_geometry_endpoint_only":
        raise RuntimeError("P14 source-level fixed-geometry calculation is not authorized")
    memory_before = available_memory_mib()
    required = float(production["required_available_memory_mib"])
    if memory_before < required:
        raise MemoryError(
            f"P14 requires {required:.0f} MiB available; observed {memory_before:.0f} MiB"
        )

    source = protocol["source_anchors_B3LYP_6_31G_star"]
    r_ch = float(production["fixed_CH_angstrom"])
    g_atoms = d3h_atoms(source["G"], r_ch)
    plg_atoms = d3h_atoms(source["PLG"], r_ch)
    ordinary_g, _g_density = ordinary_state(g_atoms, production)
    ordinary_plg, plg_density = ordinary_state(plg_atoms, production)
    if not ordinary_g["converged"] or not ordinary_plg["converged"]:
        raise RuntimeError("P14 source-level ordinary anchor did not converge")
    write_json(
        checkpoint_path,
        {
            "schema_version": 1,
            "protocol_id": protocol["protocol_id"],
            "stage": "ordinary_source_anchors_complete_conditional_pending",
            "ordinary_G": ordinary_g,
            "ordinary_at_PLG": ordinary_plg,
            "memory_before_mib": memory_before,
        },
    )
    del _g_density
    gc.collect()
    conditional_plg_raw = conditional_state(
        plg_atoms, production, classes, plg_density
    )
    conditional_plg = compact_state(conditional_plg_raw)

    fixed_endpoint = (
        float(ordinary_g["total_energy_hartree"])
        - float(conditional_plg["total_energy_hartree"])
    ) * HARTREE_TO_KCAL_PER_MOL
    source_endpoint = float(source["delta_E_GP_kcal_mol"])
    comparisons = {
        "G_source_energy_hartree": float(source["G"]["energy_hartree"]),
        "G_energy_residual_hartree": float(ordinary_g["total_energy_hartree"]) - float(source["G"]["energy_hartree"]),
        "PLG_source_energy_hartree": float(source["PLG"]["energy_hartree"]),
        "PLG_energy_residual_hartree": float(conditional_plg["total_energy_hartree"]) - float(source["PLG"]["energy_hartree"]),
        "source_delta_E_GP_kcal_mol": source_endpoint,
        "fixed_endpoint_residual_kcal_mol": fixed_endpoint - source_endpoint,
    }
    checks = {
        "ordinary_G_converged": bool(ordinary_g["converged"]),
        "ordinary_at_PLG_converged": bool(ordinary_plg["converged"]),
        "conditional_PLG_converged": bool(conditional_plg["converged"]),
        "ordinary_G_78_electrons": abs(float(ordinary_g["physical_metric_electron_count"]) - 78.0) <= 1.0e-7,
        "ordinary_at_PLG_78_electrons": abs(float(ordinary_plg["physical_metric_electron_count"]) - 78.0) <= 1.0e-7,
        "conditional_PLG_78_electrons": abs(float(conditional_plg["masked_metric_electron_count"]) - 78.0) <= 1.0e-7,
        "single_tensor_memory_mode": conditional_plg["eri_storage_mode"] == "single_tensor_inplace_category_mask",
        "energy_components_close": float(conditional_plg["energy_component_closure_residual_hartree"]) <= 1.0e-9,
        "commutator_closed": float(conditional_plg["final_commutator_frobenius_norm"]) <= 1.0e-5,
        "density_idempotent": float(conditional_plg["closed_shell_idempotency_relative_residual"]) <= 1.0e-7,
        "endpoint_positive": fixed_endpoint > 0.0,
        "scientific_classification_deferred": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    record = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "stage": "source_level_fixed_geometry_anchor",
        "method": {
            "engine": "PySCF",
            "pyscf_xc": production["pyscf_xc"],
            "basis": production["basis"],
            "grid_level": production["grid_level"],
            "original_program_code_used": False,
            "fit_to_published_values": False,
        },
        "geometry_contract": {
            "G": {"atoms_angstrom": g_atoms, "metrics": geometry_metrics(g_atoms)},
            "PLG": {"atoms_angstrom": plg_atoms, "metrics": geometry_metrics(plg_atoms)},
            "fixed_CH_angstrom": r_ch,
            "CH_coordinate_status": production["CH_coordinate_status"],
        },
        "ordinary_G": ordinary_g,
        "ordinary_at_PLG": ordinary_plg,
        "conditional_PLG": conditional_plg,
        "fixed_geometry_endpoint_kcal_mol": fixed_endpoint,
        "source_comparison": comparisons,
        "acceptance_checks": checks,
        "anchor_gate_verdict": "PASS" if all(checks.values()) else "FAIL",
        "memory_before_mib": memory_before,
        "peak_rss_mib": float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0,
        "wall_time_seconds": time.perf_counter() - started,
        "scientific_classification_allowed": False,
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
    print(json.dumps({
        "verdict": record["anchor_gate_verdict"],
        "fixed_geometry_endpoint_kcal_mol": record["fixed_geometry_endpoint_kcal_mol"],
        "G_energy_residual_hartree": record["source_comparison"]["G_energy_residual_hartree"],
        "PLG_energy_residual_hartree": record["source_comparison"]["PLG_energy_residual_hartree"],
        "wall_time_seconds": record["wall_time_seconds"],
        "peak_rss_mib": record["peak_rss_mib"],
        "output": str(arguments.output),
    }, ensure_ascii=False), flush=True)
    return 0 if record["anchor_gate_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
