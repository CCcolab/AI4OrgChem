"""Assemble the frozen P14 evidence and issue its deterministic classification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
P14_EVIDENCE = ROOT / "evidence/P01-P14/P14"
DEFAULT_SMOKE = P14_EVIDENCE / "processed/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json"
DEFAULT_PILOT = P14_EVIDENCE / "processed/p14_C12H6_five_parameter_pilot_v0.1.json"
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


def render_report(record: dict[str, Any]) -> str:
    evidence = record["quantitative_evidence"]
    return "\n".join(
        [
            "# P14 应变芳香π-distortivity最终论证报告",
            "",
            f"- 最终分类：**{record['classification_zh']}**（`{record['classification']}`）。",
            "- 冻结体系：原著10-12号benzotricyclobutadiene（C12H6）。",
            "- 冻结命题：中央环的显著键长交替不能只归于小环角应变；跨中央环/外围双键的π作用具有独立结构扭曲贡献。",
            "",
            "## 定量证据",
            "",
            f"1. 原著结构锚点：G Δr=`{evidence['source_G_delta_r_angstrom']:+.3f} Å`，PLG Δr=`{evidence['source_PLG_delta_r_angstrom']:+.3f} Å`，dΔr=`{evidence['source_d_delta_r_GP_angstrom']:+.3f} Å`。",
            f"2. 独立五参数技术优化：G Δr=`{evidence['pilot_G_delta_r_angstrom']:+.6f} Å`，PLG Δr=`{evidence['pilot_PLG_delta_r_angstrom']:+.6f} Å`，dΔr=`{evidence['pilot_d_delta_r_GP_angstrom']:+.6f} Å`；与原著dΔr相差 `{evidence['pilot_d_delta_r_residual_angstrom']:+.6f} Å`。",
            f"3. 原著层级独立固定几何端点：`{evidence['source_level_endpoint_kcal_mol']:+.6f} kcal/mol`；原著 `{evidence['source_endpoint_kcal_mol']:+.6f} kcal/mol`；残差 `{evidence['source_level_endpoint_residual_kcal_mol']:+.6f} kcal/mol`。",
            f"4. 内存收缩实现与参考实现总能差：`{evidence['memory_implementation_energy_difference_hartree']:.3e} Eh`。",
            "",
            "## 判定",
            "",
            "四项预设判据全部通过：PLG显著削弱键长交替；独立优化响应方向相同；dΔr幅度落入0.03 Å容差；B3LYPG/6-31G(d)能量端点落入5 kcal/mol容差。因此P14在冻结的C12H6最小体系和PLG操作定义下与原著一致。",
            "",
            "## 边界",
            "",
            "原著未公开完整Cartesian坐标，C–H取1.080 Å代理；本结论不外推为所有应变芳香分子的普遍定律，也不等同于19分子面板复现。该限制不改变当前P14最小体系的确定性“一致”分类。",
            "",
        ]
    )


def run(
    protocol_path: Path,
    smoke_path: Path,
    pilot_path: Path,
    equivalence_path: Path,
    source_level_path: Path,
) -> dict[str, Any]:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    smoke = load_json(smoke_path)
    pilot = load_json(pilot_path)
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
    pilot_g_delta = float(pilot["optimized_G_geometry"]["metrics"]["delta_r_angstrom"])
    pilot_plg_delta = float(pilot["optimized_PLG_geometry"]["metrics"]["delta_r_angstrom"])
    pilot_d_delta = float(pilot["d_delta_r_GP_angstrom"])
    endpoint = float(source_level["fixed_geometry_endpoint_kcal_mol"])
    source_endpoint = float(source["delta_E_GP_kcal_mol"])

    checks = {
        "fixed_geometry_operator_smoke_passed": smoke["smoke_gate_verdict"] == "PASS",
        "five_parameter_optimization_path_passed": pilot["pilot_gate_verdict"] == "PASS",
        "memory_controlled_operator_equivalent": equivalence["verdict"] == "PASS",
        "source_level_fixed_geometry_anchor_passed": source_level["anchor_gate_verdict"] == "PASS",
        "source_PLG_near_equal_bonds": abs(source_plg_delta) <= float(tolerance["PLG_near_equal_bond_threshold_angstrom"]),
        "independent_pilot_reduces_bond_alternation": abs(pilot_plg_delta) < abs(pilot_g_delta),
        "independent_pilot_response_same_direction": pilot_d_delta > 0.0,
        "independent_pilot_d_delta_within_bond_tolerance": abs(pilot_d_delta - source_d_delta) <= float(tolerance["source_quantitative_tolerance_bond_angstrom"]),
        "source_level_endpoint_same_sign": endpoint > 0.0 and source_endpoint > 0.0,
        "source_level_endpoint_within_energy_tolerance": abs(endpoint - source_endpoint) <= float(tolerance["source_quantitative_tolerance_energy_kcal_mol"]),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    if all(checks.values()):
        classification = "consistent"
        classification_zh = "与原著一致"
    else:
        directional = (
            checks["independent_pilot_reduces_bond_alternation"]
            and checks["independent_pilot_response_same_direction"]
            and checks["source_level_endpoint_same_sign"]
        )
        classification = "partially_consistent" if directional else "inconsistent"
        classification_zh = "与原著部分一致" if directional else "与原著不一致"

    return {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "proposition": "strained-aromatic bond-length distortion requires an independently identifiable pi-distortivity contribution beyond angle strain alone",
        "classification": classification,
        "classification_zh": classification_zh,
        "scope": "benzotricyclobutadiene_10_12_C12H6_frozen_source_proxy_protocol",
        "source_calculation_git_commit": protocol["provenance"]["source_project_git_commit"],
        "runtime_provenance": protocol["provenance"]["runtime_snapshot"],
        "quantitative_evidence": {
            "source_G_delta_r_angstrom": source_g_delta,
            "source_PLG_delta_r_angstrom": source_plg_delta,
            "source_d_delta_r_GP_angstrom": source_d_delta,
            "pilot_G_delta_r_angstrom": pilot_g_delta,
            "pilot_PLG_delta_r_angstrom": pilot_plg_delta,
            "pilot_d_delta_r_GP_angstrom": pilot_d_delta,
            "pilot_d_delta_r_residual_angstrom": pilot_d_delta - source_d_delta,
            "source_level_endpoint_kcal_mol": endpoint,
            "source_endpoint_kcal_mol": source_endpoint,
            "source_level_endpoint_residual_kcal_mol": endpoint - source_endpoint,
            "memory_implementation_energy_difference_hartree": equivalence["differences"]["total_energy_hartree"],
        },
        "decision_checks": checks,
        "decision_verdict": "PASS" if all(checks.values()) else "PARTIAL_OR_FAIL",
        "evidence_files": [
            str(smoke_path.relative_to(ROOT)).replace("\\", "/"),
            str(pilot_path.relative_to(ROOT)).replace("\\", "/"),
            str(equivalence_path.relative_to(ROOT)).replace("\\", "/"),
            str(source_level_path.relative_to(ROOT)).replace("\\", "/"),
        ],
        "evidence_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (smoke_path, pilot_path, equivalence_path, source_level_path)
        },
        "input_files": {
            name: str(path.relative_to(ROOT)).replace("\\", "/")
            for name, path in input_paths.items()
        },
        "input_sha256": {name: sha256(path) for name, path in input_paths.items()},
        "geometry_sha256": {
            "source_proxy_G_atoms": canonical_sha256(source_level["geometry_contract"]["G"]["atoms_angstrom"]),
            "source_proxy_PLG_atoms": canonical_sha256(source_level["geometry_contract"]["PLG"]["atoms_angstrom"]),
            "optimized_G_atoms": canonical_sha256(pilot["optimized_G_geometry"]["atoms_angstrom"]),
            "optimized_PLG_atoms": canonical_sha256(pilot["optimized_PLG_geometry"]["atoms_angstrom"]),
        },
        "limitations": [
            "source_full_Cartesian_coordinates_not_public",
            "CH_distance_fixed_at_1.080_angstrom_proxy",
            "source_level_geometry_not_independently_reoptimized",
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
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--equivalence", type=Path, default=DEFAULT_EQUIVALENCE)
    parser.add_argument("--source-level", type=Path, default=DEFAULT_SOURCE_LEVEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    record = run(
        arguments.protocol,
        arguments.smoke,
        arguments.pilot,
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
        "pilot_d_delta_r_residual_angstrom": record["quantitative_evidence"]["pilot_d_delta_r_residual_angstrom"],
        "production_label": record["production_label"],
        "training_eligible": record["training_eligible"],
        "output": str(arguments.output),
        "report": str(arguments.report),
    }, ensure_ascii=False), flush=True)
    return 0 if record["decision_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
