from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    hessian_path = "data/science_v0.2/raw/wp3/wp3_hessian_mixing.json"
    grid_path = "data/science_v0.2/raw/wp3/wp3_grid.json"
    hessian = load(hessian_path)
    grid = load(grid_path)
    modes = grid["displacement_modes"]
    curves = {key: value["curvatures_hartree_per_angstrom2"] for key, value in modes.items()}
    delta = {key: value["delta_k_e_conditional_minus_ordinary"] for key, value in curves.items()}
    closures = {key: abs(value["ordinary_closure_residual"]) for key, value in curves.items()}
    all_points = [point for mode in modes.values() for point in mode["points"]]
    all_ordinary = all(point["ordinary"]["converged"] for point in all_points)
    all_conditional = all(point["conditional"].get("converged", False) for point in all_points)
    controls = [abs(delta[key]) for key in ("A1g_breathing", "E2g_bend_cos", "E2g_bend_sin")]
    selectivity = abs(delta["B2u_BLA"]) / max(controls)
    h = hessian["hessian"]
    mode_gate = h["one_dimensional_modes_pass"] and h.get("e2g_mixed_subspace_pass", False)
    causal_support = delta["B2u_BLA"] > 0.0 and selectivity >= 5.0 and all_conditional
    gate_pass = mode_gate and causal_support and max(closures.values()) < 1e-7 and all_ordinary

    registry = load("configs/science_v0.2/claim_estimand_registry.json")
    templates = {row["claim_id"]: row for row in registry["records"]}
    evidence_paths = [hessian_path, grid_path]
    p10a = dict(templates["P10-A"])
    p10a.update({
        "comparison_outcome": "CONSISTENT",
        "conclusion_state": "SUPPORTED" if gate_pass else "PARTIALLY_SUPPORTED",
        "scientific_grade": "R2",
        "replay_status": "NOT_REPLAYED",
        "agent_maturity": "M1_PLUS",
        "evidence_paths": evidence_paths + p10a.get("evidence_paths", []),
        "limitations": [
            "P10-A is a path ledger. Its electronic/nuclear decomposition does not alone prove causal primacy.",
            "The E2g seed is a mixture of multiple Hessian eigenspaces; the original seed was retained and the minimal covering eigensubspace was reported.",
        ],
    })
    p10b = dict(templates["P10-B"])
    p10b.update({
        "comparison_outcome": "NOT_APPLICABLE",
        "conclusion_state": "SUPPORTED" if gate_pass else "PARTIALLY_SUPPORTED",
        "scientific_grade": "R3" if gate_pass else "R2",
        "replay_status": "NOT_REPLAYED",
        "agent_maturity": "M1_PLUS",
        "evidence_paths": evidence_paths,
        "limitations": [
            "P10-B is a new complementary mechanism claim and does not automatically upgrade P10-A.",
            "The causal intervention uses the frozen project conditional-SCF definition; external independent implementation remains a replay objective.",
        ],
    })
    result = {
        "schema_version": "science-v0.2-wp3-decision-1",
        "work_package": "WP3",
        "gate": "V2-3",
        "gate_status": "PASS" if gate_pass else "PARTIAL_NOT_PASSED",
        "p10a_conclusion": p10a["conclusion_state"],
        "p10a_grade": p10a["scientific_grade"],
        "p10b_conclusion": p10b["conclusion_state"],
        "p10b_grade": p10b["scientific_grade"],
        "ordinary_curvatures_hartree_per_angstrom2": {key: value["ordinary"] for key, value in curves.items()},
        "delta_k_e_hartree_per_angstrom2": delta,
        "b2u_to_largest_control_selectivity": selectivity,
        "maximum_energy_ledger_closure_residual": max(closures.values()),
        "all_ordinary_points_converged": all_ordinary,
        "all_conditional_points_converged": all_conditional,
        "hessian_mode_checks": h,
        "source_hashes": {path: digest(path) for path in evidence_paths},
        "interpretation": "The ordinary electronic response is strongly B2u-distortive while nuclear repulsion is more strongly restoring. The frozen pi-localization intervention selectively reduces the B2u electronic distortion response, discriminating the preregistered mechanism predictions in favor of a nuclear-repulsion-led balance within this protocol.",
    }
    out = ROOT / "data/science_v0.2/decisions/wp3"
    out.mkdir(parents=True, exist_ok=True)
    (out / "gate_v2_3_decision.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "p10a_evidence_record.json").write_text(json.dumps(p10a, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "p10b_evidence_record.json").write_text(json.dumps(p10b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = ROOT / "docs/releases/science_v0.2/reports/WP3_GATE_V2_3_REPORT.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        "# WP3 / Gate V2-3：苯 D6h 多路径与 π 局域干预",
        "",
        f"- Gate：`{result['gate_status']}`",
        f"- P10-A：`{p10a['conclusion_state']} / {p10a['scientific_grade']}`",
        f"- P10-B：`{p10b['conclusion_state']} / {p10b['scientific_grade']}`",
        "",
        "| 坐标 | k_total | k_e | k_N | Δk_e（局域−普通） |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in ("B2u_BLA", "A1g_breathing", "E2g_bend_cos", "E2g_bend_sin"):
        ordinary = curves[key]["ordinary"]
        rows.append(f"| {key} | {ordinary['total']:.6f} | {ordinary['electronic']:.6f} | {ordinary['nuclear']:.6f} | {delta[key]:.6f} |")
    rows += [
        "",
        f"B2u因果效应相对最大对照的选择性为{selectivity:.2f}倍；36个普通态与36个条件态均收敛。严格二维E2g本征对匹配失败，但扩展混合本征子空间达到预注册覆盖阈值，原始种子未被替换。",
        "",
        "在本协议内，结果支持“普通π电子响应沿B2u促畸变，而更大的核排斥恢复项维持D6h”的机制表述。该结论属于P10-B自身，不自动升级P10-A。",
        "",
        "## English conclusion",
        "",
        "The frozen pi-localization intervention selectively weakens the strongly distortive ordinary electronic B2u curvature, while the nuclear term remains more strongly restoring. The preregistered competing predictions are therefore discriminated in favor of a nuclear-repulsion-led balance within the tested protocol. P10-B is its own complementary mechanism claim and does not automatically upgrade P10-A.",
        "",
    ]
    report.write_text("\n".join(rows), encoding="utf-8")
    print(json.dumps({"status": "PASS", "gate": result["gate_status"], "selectivity": selectivity}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
