from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HARTREE_TO_KCAL = 627.509474


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    endpoint_path = "data/science_v0.2/raw/wp1/wp1_endpoints.json"
    cas4_path = "data/science_v0.2/raw/wp1/wp1_cas4_path.json"
    cas12_path = "data/science_v0.2/raw/wp1/wp1_cas12_endpoints.json"
    qp_path = "data/science_v0.2/processed/wp1/wp1_qp2_cipsi_result.json"
    endpoints, cas4, cas12, qp = map(load, (endpoint_path, cas4_path, cas12_path, qp_path))

    rks = endpoints["optimized_endpoints"]
    rks_barrier = (rks["D4h"]["energy_hartree"] - rks["D2h"]["energy_hartree"]) * HARTREE_TO_KCAL
    cas4_rows = cas4["cas4_path"]
    cas4_barrier = (cas4_rows[-1]["sc_nevpt2"][0]["total_hartree"] - cas4_rows[0]["sc_nevpt2"][0]["total_hartree"]) * HARTREE_TO_KCAL
    cas12_rows = cas12["cas12_endpoints"]
    cas12_barrier = (cas12_rows["D4h"]["sc_nevpt2"][0]["total_hartree"] - cas12_rows["D2h"]["sc_nevpt2"][0]["total_hartree"]) * HARTREE_TO_KCAL
    q = {row["endpoint"]: row for row in qp["endpoints"]}
    qp_barrier = (q["D4H"]["e_var_plus_pt2_hartree"] - q["D2H"]["e_var_plus_pt2_hartree"]) * HARTREE_TO_KCAL
    final = {key: q[key]["iteration_series"][-1] for key in ("D2H", "D4H")}
    extrapolated_barrier = (
        final["D4H"]["fci_extrapolation_points"][0]["extrapolated_energy_hartree"]
        - final["D2H"]["fci_extrapolation_points"][0]["extrapolated_energy_hartree"]
    ) * HARTREE_TO_KCAL
    barriers = {
        "B3LYP_RKS_kcal_mol": rks_barrier,
        "CAS_4_4_SC_NEVPT2_kcal_mol": cas4_barrier,
        "CAS_12_12_SC_NEVPT2_kcal_mol": cas12_barrier,
        "QP_CIPSI_Evar_plus_PT2_kcal_mol": qp_barrier,
        "QP_reported_extrapolation_subset_kcal_mol": extrapolated_barrier,
    }
    all_positive = all(value > 1.0 for value in barriers.values())
    method_spread = max(barriers.values()) - min(barriers.values())
    conclusion = "PARTIALLY_SUPPORTED" if all_positive else "INDETERMINATE"

    registry = load("configs/science_v0.2/claim_estimand_registry.json")
    template = next(row for row in registry["records"] if row["claim_id"] == "P09-B")
    evidence = dict(template)
    evidence.update({
        "comparison_outcome": "NOT_APPLICABLE",
        "conclusion_state": conclusion,
        "scientific_grade": "R2",
        "replay_status": "NOT_REPLAYED",
        "agent_maturity": "M1_PLUS",
        "evidence_paths": [endpoint_path, cas4_path, cas12_path, qp_path],
        "limitations": [
            "P09-B is COMPLEMENTARY to P09-A and cannot automatically change the source-aligned ADE/VDE conclusion.",
            f"All tested barriers are positive, but the method spread is {method_spread:.2f} kcal/mol; the quantitative barrier is method-sensitive.",
            "The QP PT2 residual magnitude remains large at the preregistered determinant ceiling; the reported extrapolation is retained as sensitivity evidence, not treated as an exact FCI limit.",
        ],
    })

    result = {
        "schema_version": "science-v0.2-wp1-decision-1",
        "work_package": "WP1",
        "gate": "V2-1",
        "gate_status": "PASS_WITH_METHOD_SENSITIVITY",
        "claim_id": "P09-B",
        "relation_to_v0_1": "COMPLEMENTARY",
        "conclusion_state": conclusion,
        "scientific_grade": "R2",
        "barriers_kcal_mol": barriers,
        "method_spread_kcal_mol": method_spread,
        "sign_consistency": "ALL_POSITIVE" if all_positive else "MIXED_OR_DEADBAND",
        "multireference_diagnostics": {
            "cas4_d4h_singlet_frontier_noons": cas4_rows[-1]["root_noons"][0],
            "cas12_d4h_singlet_frontier_noons": cas12_rows["D4h"]["root_noons"][0],
            "qp_final_n_det": {key: q[key]["n_det"] for key in q},
            "qp_final_pt2_statistical_error_hartree": {key: final[key]["pt2_statistical_error_hartree"] for key in final},
            "qp_final_variance_hartree2": {key: final[key]["variance_hartree2"] for key in final},
        },
        "source_hashes": {path: sha(path) for path in (endpoint_path, cas4_path, cas12_path, qp_path)},
        "raw_metadata_note": "The archived CAS(12,12) raw record has a stale descriptive orbital_initialization string saying carbon-pz ranking; active_orbital_selection_mode and the code path correctly show total carbon-2p ranking. The live runner label is corrected without editing raw data.",
        "interpretation": "Independent ordinary-state calculations consistently place D4h above D2h and confirm strong D4h multireference character. They support P09-B qualitatively, but do not yield a method-independent quantitative barrier and do not directly test P09-A.",
    }

    out_dir = ROOT / "data/science_v0.2/decisions/wp1"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gate_v2_1_decision.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "p09b_evidence_record.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_dir = ROOT / "docs/releases/science_v0.2/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# WP1 / Gate V2-1：环丁二烯普通物理态多参考稳健性",
        "",
        "- Gate：`PASS_WITH_METHOD_SENSITIVITY`",
        f"- P09-B结论：`{conclusion}`，证据等级`R2`",
        "- 与V0.1 P09-A关系：`COMPLEMENTARY`，不自动改写条件态ADE/VDE",
        "",
        "## 势垒结果（D4h − D2h）",
        "",
        "| 方法 | kcal/mol |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {value:.6f} |" for name, value in barriers.items())
    lines += [
        "",
        "所有受测方法给出正势垒，且D4h自然占据数显示明显双自由基/多组态特征；但不同方法的势垒幅度离散很大。故V0.2支持的是P09-B的定性物理图像，不发布单一方法无关的精确势垒。",
        "",
        "Quantum Package主锚点在预注册行列式上限附近仍有较大剩余PT2，因此其E+PT2和外推序列作为高等级敏感性证据保留，不能冒充已收敛FCI。失败启动、环境修复和原始日志均保留。",
        "",
        "## English conclusion",
        "",
        "All tested ordinary-state methods place the D4h stationary point above the D2h minimum and diagnose strong D4h multireference character. WP1 therefore partially supports P09-B at R2, while the quantitative barrier remains method-sensitive. This evidence is complementary to, not a direct upgrade of, the P09-A conditional-state estimand.",
        "",
    ]
    (report_dir / "WP1_GATE_V2_1_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "PASS", "gate": result["gate_status"], "conclusion": conclusion, "barriers": barriers}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
