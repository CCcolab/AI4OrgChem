"""Assemble the frozen P14 evidence and issue its deterministic classification."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
P14_EVIDENCE = ROOT / "evidence/P01-P14/P14"
DEFAULT_SMOKE = P14_EVIDENCE / "processed/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json"
DEFAULT_OPTIMIZATION = P14_EVIDENCE / "processed/p14_C12H6_B3LYPG_6_31Gd_production_optimization_v0.1.json"
DEFAULT_EQUIVALENCE = P14_EVIDENCE / "processed/p14_memory_controlled_eri_equivalence_v0.1.json"
DEFAULT_SOURCE_LEVEL = P14_EVIDENCE / "processed/p14_C12H6_source_level_fixed_geometry_v0.1.json"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_strained_aromatic_pi_distortivity_classification_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_strained_aromatic_pi_distortivity_final.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def assess_optimization_eligibility(protocol: dict[str, Any], record: dict[str, Any]) -> dict[str, bool]:
    """Apply the scientific gate to a five-parameter geometry-optimization record.

    Optimizer ``success`` alone is deliberately insufficient: SciPy may stop on
    function-value stagnation while the gradient still exceeds the preregistered
    threshold.  A technical pilot that explicitly disables scientific
    classification must never be promoted to proposition evidence.
    """

    production = protocol["production_calculation"]
    tolerance = float(
        production.get("geometry_optimizer", {}).get(
            "gradient_tolerance_hartree_per_angstrom",
            protocol["five_parameter_pilot"]["optimizer"]["gradient_tolerance_hartree_per_angstrom"],
        )
    )
    expected_basis = str(production["basis"]).lower()
    method = record.get("method", {})
    g_opt = record.get("G_optimizer", {})
    plg_opt = record.get("PLG_optimizer", {})
    allowed_terminations = {"gradient_tolerance_satisfied", "projected_gradient_tolerance_satisfied"}

    def number_close(value: Any, target: float, tolerance_value: float) -> bool:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return False
        return math.isfinite(numeric) and abs(numeric - target) <= tolerance_value

    def gradient_ok(item: dict[str, Any]) -> bool:
        value = item.get("gradient_max_abs_hartree_per_angstrom")
        return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) <= tolerance

    def termination_ok(item: dict[str, Any]) -> bool:
        reason = str(item.get("termination_reason", "")).strip().lower()
        # A verified gradient below threshold is decisive even if a third-party
        # optimizer reports a generic success message.
        return reason in allowed_terminations or gradient_ok(item)

    return {
        "optimization_scientific_classification_allowed": record.get("scientific_classification_allowed") is True,
        "optimization_protocol_id_matches": record.get("protocol_id") == protocol.get("protocol_id"),
        "optimization_protocol_authorized": production.get("geometry_optimization_authorized") is True,
        "optimization_stage_is_production": "production" in str(record.get("stage", "")).lower(),
        "optimization_method_matches": str(method.get("pyscf_xc", "")).upper() == str(production["pyscf_xc"]).upper(),
        "optimization_basis_matches": str(method.get("basis", "")).lower() == expected_basis,
        "optimization_grid_matches": method.get("grid_level") == production["grid_level"],
        "G_optimizer_success": g_opt.get("success") is True,
        "G_gradient_within_tolerance": gradient_ok(g_opt),
        "G_termination_qualified": termination_ok(g_opt),
        "G_no_active_bound": not g_opt.get("active_bounds", []),
        "G_state_converged": record.get("G_state", {}).get("converged") is True,
        "G_78_electrons": number_close(record.get("G_state", {}).get("physical_metric_electron_count"), 78.0, 1.0e-7),
        "PLG_optimizer_success": plg_opt.get("success") is True,
        "PLG_gradient_within_tolerance": gradient_ok(plg_opt),
        "PLG_termination_qualified": termination_ok(plg_opt),
        "PLG_no_active_bound": not plg_opt.get("active_bounds", []),
        "PLG_state_converged": record.get("PLG_state", {}).get("converged") is True,
        "PLG_78_electrons": number_close(record.get("PLG_state", {}).get("physical_metric_electron_count"), 78.0, 1.0e-7),
    }


def render_report(record: dict[str, Any]) -> str:
    evidence = record["quantitative_evidence"]
    if record["classification"] == "consistent":
        maintenance_note = (
            "> **v0.3.1维护说明（2026-09-08）：** 外部复评指出v0.3.0误用了不具科学资格的STO-3G技术烟测。"
            "修复后的分类器已拒绝该记录；新增B3LYPG/6-31G(d)生产优化通过全部注册门禁后，P14才恢复为“一致”。"
        )
        boundary_tail = (
            "本次G/PLG优化只覆盖预注册的平面D3h五参数子空间；未宣称完成全笛卡尔频率分析或更宽对称性搜索。"
        )
    else:
        maintenance_note = (
            "> **v0.3.1维护说明（2026-09-08）：** 本报告按外部复评修正P14证据资格门禁。"
            "v0.3.0中的STO-3G五参数记录仅是技术烟测，不具科学定判资格；在生产级优化闭合前，P14暂定为“部分一致”。"
        )
        boundary_tail = (
            "只有同协议B3LYPG/6-31G(d)的G/PLG生产级优化同时通过授权、梯度、终止原因、电子数和边界检查，"
            "才可恢复为确定性“一致”分类。"
        )
    return "\n".join(
        [
            maintenance_note,
            "",
            "# P14 应变芳香π-distortivity最终论证报告",
            "",
            f"- 最终分类：**{record['classification_zh']}**（`{record['classification']}`）。",
            "- 冻结体系：原著10-12号benzotricyclobutadiene（C12H6）。",
            "- 冻结命题：中央环的显著键长交替不能只归于小环角应变；跨中央环/外围双键的π作用具有独立结构扭曲贡献。",
            "",
            "## 定量证据",
            "",
            f"1. 原著结构锚点：G Δr=`{evidence['source_G_delta_r_angstrom']:+.3f} Å`，PLG Δr=`{evidence['source_PLG_delta_r_angstrom']:+.3f} Å`，dΔr=`{evidence['source_d_delta_r_GP_angstrom']:+.3f} Å`。",
            f"2. {record['optimization_evidence_label_zh']}：G Δr=`{evidence['optimization_G_delta_r_angstrom']:+.6f} Å`，PLG Δr=`{evidence['optimization_PLG_delta_r_angstrom']:+.6f} Å`，dΔr=`{evidence['optimization_d_delta_r_GP_angstrom']:+.6f} Å`；与原著dΔr相差 `{evidence['optimization_d_delta_r_residual_angstrom']:+.6f} Å`。",
            f"3. 生产优化端点：`{evidence['optimization_endpoint_kcal_mol']:+.6f} kcal/mol`；原著 `{evidence['source_endpoint_kcal_mol']:+.6f} kcal/mol`；残差 `{evidence['optimization_endpoint_residual_kcal_mol']:+.6f} kcal/mol`。",
            f"4. 原著层级独立固定几何端点：`{evidence['source_level_endpoint_kcal_mol']:+.6f} kcal/mol`；残差 `{evidence['source_level_endpoint_residual_kcal_mol']:+.6f} kcal/mol`。",
            f"5. 内存收缩实现与参考实现总能差：`{evidence['memory_implementation_energy_difference_hartree']:.3e} Eh`。",
            "",
            "## 判定",
            "",
            record["decision_summary_zh"],
            "",
            "## 边界",
            "",
            "原著未公开完整Cartesian坐标，C–H取1.080 Å代理；本结论不外推为所有应变芳香分子的普遍定律，也不等同于19分子面板复现。"
            + boundary_tail,
            "",
        ]
    )


def run(
    protocol_path: Path,
    smoke_path: Path,
    optimization_path: Path,
    equivalence_path: Path,
    source_level_path: Path,
) -> dict[str, Any]:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    smoke = load_json(smoke_path)
    optimization = load_json(optimization_path)
    equivalence = load_json(equivalence_path)
    source_level = load_json(source_level_path)
    source = protocol["source_anchors_B3LYP_6_31G_star"]
    tolerance = protocol["final_classification"]
    input_paths = {
        name: ROOT / relative
        for name, relative in protocol["public_inputs"].items()
    }

    source_g_delta = float(source["G"]["delta_r_angstrom"])
    source_plg_delta = float(source["PLG"]["delta_r_angstrom"])
    source_d_delta = float(source["d_delta_r_GP_angstrom"])
    optimization_g_delta = float(optimization["optimized_G_geometry"]["metrics"]["delta_r_angstrom"])
    optimization_plg_delta = float(optimization["optimized_PLG_geometry"]["metrics"]["delta_r_angstrom"])
    optimization_d_delta = float(optimization["d_delta_r_GP_angstrom"])
    endpoint = float(source_level["fixed_geometry_endpoint_kcal_mol"])
    optimization_endpoint_value = optimization.get("optimized_endpoint_kcal_mol")
    if optimization_endpoint_value is None:
        optimization_endpoint_value = optimization["technical_endpoint_kcal_mol"]
    optimization_endpoint = float(optimization_endpoint_value)
    source_endpoint = float(source["delta_E_GP_kcal_mol"])
    optimization_checks = assess_optimization_eligibility(protocol, optimization)
    optimization_qualified = all(optimization_checks.values())

    checks = {
        "fixed_geometry_operator_smoke_passed": smoke["smoke_gate_verdict"] == "PASS",
        "five_parameter_optimization_record_passed_its_gate": optimization.get(
            "production_gate_verdict", optimization.get("pilot_gate_verdict")
        ) == "PASS",
        "five_parameter_production_optimization_qualified": optimization_qualified,
        "memory_controlled_operator_equivalent": equivalence["verdict"] == "PASS",
        "source_level_fixed_geometry_anchor_passed": source_level["anchor_gate_verdict"] == "PASS",
        "source_PLG_near_equal_bonds": abs(source_plg_delta) <= float(tolerance["PLG_near_equal_bond_threshold_angstrom"]),
        "optimization_reduces_bond_alternation": abs(optimization_plg_delta) < abs(optimization_g_delta),
        "optimization_response_same_direction": optimization_d_delta > 0.0,
        "optimization_d_delta_within_bond_tolerance": abs(optimization_d_delta - source_d_delta) <= float(tolerance["source_quantitative_tolerance_bond_angstrom"]),
        "optimization_endpoint_same_sign": optimization_endpoint > 0.0 and source_endpoint > 0.0,
        "optimization_endpoint_within_energy_tolerance": abs(optimization_endpoint - source_endpoint) <= float(tolerance["source_quantitative_tolerance_energy_kcal_mol"]),
        "source_level_endpoint_same_sign": endpoint > 0.0 and source_endpoint > 0.0,
        "source_level_endpoint_within_energy_tolerance": abs(endpoint - source_endpoint) <= float(tolerance["source_quantitative_tolerance_energy_kcal_mol"]),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    if all(checks.values()):
        classification = "consistent"
        classification_zh = "与原著一致"
    else:
        directional = (
            checks["optimization_reduces_bond_alternation"]
            and checks["optimization_response_same_direction"]
            and checks["source_level_endpoint_same_sign"]
        )
        classification = "partially_consistent" if directional else "inconsistent"
        classification_zh = "与原著部分一致" if directional else "与原著不一致"

    if classification == "consistent":
        decision_summary_zh = (
            "固定几何端点、算符实现和生产级五参数优化均通过预注册门禁；"
            "P14在冻结的C12H6最小体系和PLG操作定义下与原著一致。"
        )
    elif classification == "partially_consistent":
        if "technical_pilot" in str(optimization.get("stage", "")):
            qualification_reason = (
                "但现有五参数记录是STO-3G技术烟测，明确禁止科学定判，且G/PLG最大梯度均超过预注册阈值。"
            )
        else:
            failed = [name for name, passed in optimization_checks.items() if not passed]
            qualification_reason = "但生产优化尚未通过全部资格门禁：" + "、".join(failed) + "。"
        decision_summary_zh = (
            "固定几何B3LYPG/6-31G(d)端点与原著同号且在能量容差内，五参数记录的结构响应方向也相同；"
            + qualification_reason
            + "因此当前只能判为与原著部分一致，不能把不合格优化写成已完成的生产优化。"
        )
    else:
        decision_summary_zh = "现有证据未通过方向性最低条件，P14判为与原著不一致。"

    return {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "proposition": "strained-aromatic bond-length distortion requires an independently identifiable pi-distortivity contribution beyond angle strain alone",
        "classification": classification,
        "classification_zh": classification_zh,
        "decision_summary_zh": decision_summary_zh,
        "optimization_evidence_stage": optimization.get("stage"),
        "optimization_evidence_label_zh": "B3LYPG/6-31G(d)五参数生产优化" if optimization_qualified else "五参数技术烟测（不具科学定判资格）",
        "scope": "benzotricyclobutadiene_10_12_C12H6_frozen_source_proxy_protocol",
        "source_calculation_git_commit": protocol["provenance"]["source_project_git_commit"],
        "runtime_provenance": protocol["provenance"]["runtime_snapshot"],
        "quantitative_evidence": {
            "source_G_delta_r_angstrom": source_g_delta,
            "source_PLG_delta_r_angstrom": source_plg_delta,
            "source_d_delta_r_GP_angstrom": source_d_delta,
            "optimization_G_delta_r_angstrom": optimization_g_delta,
            "optimization_PLG_delta_r_angstrom": optimization_plg_delta,
            "optimization_d_delta_r_GP_angstrom": optimization_d_delta,
            "optimization_d_delta_r_residual_angstrom": optimization_d_delta - source_d_delta,
            "optimization_endpoint_kcal_mol": optimization_endpoint,
            "optimization_endpoint_residual_kcal_mol": optimization_endpoint - source_endpoint,
            "source_level_endpoint_kcal_mol": endpoint,
            "source_endpoint_kcal_mol": source_endpoint,
            "source_level_endpoint_residual_kcal_mol": endpoint - source_endpoint,
            "memory_implementation_energy_difference_hartree": equivalence["differences"]["total_energy_hartree"],
        },
        "decision_checks": checks,
        "optimization_eligibility_checks": optimization_checks,
        "decision_verdict": "PASS" if all(checks.values()) else "PARTIAL_OR_FAIL",
        "evidence_files": [
            str(smoke_path.relative_to(ROOT)).replace("\\", "/"),
            str(optimization_path.relative_to(ROOT)).replace("\\", "/"),
            str(equivalence_path.relative_to(ROOT)).replace("\\", "/"),
            str(source_level_path.relative_to(ROOT)).replace("\\", "/"),
        ],
        "evidence_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (smoke_path, optimization_path, equivalence_path, source_level_path)
        },
        "input_files": {
            name: str(path.relative_to(ROOT)).replace("\\", "/")
            for name, path in input_paths.items()
        },
        "input_sha256": {name: sha256(path) for name, path in input_paths.items()},
        "geometry_sha256": {
            "source_proxy_G_atoms": canonical_sha256(source_level["geometry_contract"]["G"]["atoms_angstrom"]),
            "source_proxy_PLG_atoms": canonical_sha256(source_level["geometry_contract"]["PLG"]["atoms_angstrom"]),
            "optimized_G_atoms": canonical_sha256(optimization["optimized_G_geometry"]["atoms_angstrom"]),
            "optimized_PLG_atoms": canonical_sha256(optimization["optimized_PLG_geometry"]["atoms_angstrom"]),
        },
        "limitations": [
            "source_full_Cartesian_coordinates_not_public",
            "CH_distance_fixed_at_1.080_angstrom_proxy",
            "production_optimization_limited_to_five_parameter_planar_D3h_subspace",
            "no_full_Cartesian_frequency_or_wider_symmetry_optimization_claimed",
            "STO3G_technical_pilot_is_not_scientific_classification_evidence",
            "single_C12H6_system_does_not_establish_universal_19_molecule_law",
        ],
        "scientific_label": classification,
        "publishable_scientific_classification": True,
        "production_label": False,
        "training_eligible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--smoke", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--optimization", type=Path, default=DEFAULT_OPTIMIZATION)
    parser.add_argument("--equivalence", type=Path, default=DEFAULT_EQUIVALENCE)
    parser.add_argument("--source-level", type=Path, default=DEFAULT_SOURCE_LEVEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    record = run(
        arguments.protocol,
        arguments.smoke,
        arguments.optimization,
        arguments.equivalence,
        arguments.source_level,
    )
    write_json(arguments.output, record)
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(render_report(record), encoding="utf-8", newline="\n")
    print(json.dumps({
        "classification": record["classification"],
        "classification_zh": record["classification_zh"],
        "decision_verdict": record["decision_verdict"],
        "source_level_endpoint_residual_kcal_mol": record["quantitative_evidence"]["source_level_endpoint_residual_kcal_mol"],
        "optimization_d_delta_r_residual_angstrom": record["quantitative_evidence"]["optimization_d_delta_r_residual_angstrom"],
        "production_label": record["production_label"],
        "training_eligible": record["training_eligible"],
        "output": str(arguments.output),
        "report": str(arguments.report),
    }, ensure_ascii=False), flush=True)
    # A deterministic partial classification is a valid classifier outcome;
    # validator failures, not scientific disagreement, should control exit code.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
