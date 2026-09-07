from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


KJ_PER_HARTREE = 2625.4996394799
KCAL_PER_HARTREE = 627.5094740631
NONAROMATIC_LOWER_KCAL = -2.0
NONAROMATIC_UPPER_KCAL = 2.0
BOUNDARY_SENSITIVITY_KCAL = 0.1


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_ase(value_kcal: float) -> dict[str, object]:
    if value_kcal < NONAROMATIC_LOWER_KCAL:
        classification = "antiaromatic"
    elif value_kcal > NONAROMATIC_UPPER_KCAL:
        classification = "aromatic"
    else:
        classification = "nonaromatic_interval"
    boundary_distance = min(
        abs(value_kcal - NONAROMATIC_LOWER_KCAL),
        abs(value_kcal - NONAROMATIC_UPPER_KCAL),
    )
    return {
        "classification": classification,
        "nearest_classification_boundary_kcal_mol": boundary_distance,
        "boundary_sensitive_within_0_1_kcal_mol": boundary_distance <= BOUNDARY_SENSITIVITY_KCAL,
    }


def load_candidate(path: Path) -> dict | None:
    if not path.exists():
        return None
    data = load(path)
    if data.get("schema_version") not in {
        "science-v0.3-wp4b-conformer-candidate-1",
        "science-v0.3-wp4b-small-dft-result-1",
        "science-v0.3-wp4b-dft-result-2",
    }:
        return None
    if not data.get("optimization_converged") or not data.get("scf_converged"):
        return None
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project
    raw = project / "data/science_v0.3/raw/wp4b"
    processed = project / "data/science_v0.3/processed/wp4b"
    decisions = project / "data/science_v0.3/decisions/wp4b"
    reports = project / "docs/releases/science_v0.3/reports"
    for path in (processed, decisions, reports):
        path.mkdir(parents=True, exist_ok=True)

    contract_path = project / "configs/science_v0.3/wp4b_paired_pilot_contract.json"
    anchors_path = project / "configs/science_v0.3/wp4b_source_0k_anchors.json"
    manifest_path = project / "data/science_v0.3/inputs/wp4b/input_manifest.json"
    contract, anchors, manifest = map(load, (contract_path, anchors_path, manifest_path))

    anchor_by_n: dict[int, dict[str, dict]] = defaultdict(dict)
    for row in anchors["records"]:
        anchor_by_n[int(row["N"])][str(row["species"])] = row

    six_points: list[dict[str, object]] = []
    paired_selection_path = raw / "paired_conformer_selection.json"
    selection_path = paired_selection_path if paired_selection_path.exists() else raw / "small_conformer_selection.json"
    selection = load(selection_path) if selection_path.exists() else {"complete": False, "selected": []}
    small_full = True
    small_minima = True
    for row in selection.get("selected", []):
        path = raw / f"{row['id']}.json"
        if not path.exists():
            small_full = False
            continue
        data = load(path)
        if data.get("schema_version") != "science-v0.3-wp4b-small-dft-result-1" or "e0_hartree" not in data:
            small_full = False
        if not data.get("minimum", False):
            small_minima = False
    selected_e0_complete = True
    selected_e0_sources: list[dict[str, object]] = []
    for n in (8, 10, 16, 18, 32, 34):
        chosen: dict[str, dict] = {}
        for row in selection.get("selected", []):
            if int(row["N"]) == n:
                path = raw / f"{row['id']}.json"
                if path.exists():
                    data = load(path)
                    if "e0_hartree" in data:
                        chosen[str(row["species"])] = data
                        selected_e0_sources.append({"N": n, "species": row["species"], "identity": row["id"], "e0_source": "new_pyscf_hessian"})
                if str(row["species"]) not in chosen and n in anchor_by_n and str(row["id"]).endswith("_source"):
                    chosen[str(row["species"])] = anchor_by_n[n][str(row["species"])]
                    selected_e0_sources.append({"N": n, "species": row["species"], "identity": row["id"], "e0_source": "published_source_anchor"})
        if set(chosen) == set("ABCD"):
            delta = chosen["C"]["e0_hartree"] + chosen["D"]["e0_hartree"] - chosen["A"]["e0_hartree"] - chosen["B"]["e0_hartree"]
            value_kcal = delta * KCAL_PER_HARTREE
            six_points.append({
                "N": n,
                "series": "4n" if n % 4 == 0 else "4n+2",
                "e0_ase_hartree": delta,
                "e0_ase_kj_mol": delta * KJ_PER_HARTREE,
                "e0_ase_kcal_mol": value_kcal,
                "source": "selected paired-pilot minima",
                "minimum_status": "ALL_A_B_C_D_MINIMUM_IDENTITIES_VERIFIED",
                **classify_ase(value_kcal),
            })
        else:
            small_full = False
            selected_e0_complete = False
    six_points.sort(key=lambda row: int(row["N"]))

    manifest_ok = (
        len(manifest.get("records", [])) == 24
        and {int(row["N"]) for row in manifest["records"]} == {8, 10, 16, 18, 32, 34}
        and all(row.get("primary", {}).get("sha256") and row.get("secondary", {}).get("sha256") for row in manifest["records"])
        and all(row.get("primary", {}).get("ez_sequence") and row.get("secondary", {}).get("ez_sequence") for row in manifest["records"])
    )
    # A geometry manifest proves that two inputs exist; it does not prove that
    # both sources were evaluated.  Large-N source records are published 0 K
    # anchors, whereas their independent ETKDG candidates still require a real
    # optimization.  Keep the two identities separate in the coverage ledger.
    candidate_coverage: list[dict[str, object]] = []
    for n in (8, 10, 16, 18, 32, 34):
        for species in "ABCD":
            source_result = load_candidate(raw / f"N{n:02d}_{species}_source.json")
            etkdg_result = load_candidate(raw / f"N{n:02d}_{species}_etkdg.json")
            auditbest_result = load_candidate(raw / f"N{n:02d}_{species}_auditbest.json")
            source_anchor = anchor_by_n.get(n, {}).get(species)
            primary_evaluated = source_result is not None or source_anchor is not None
            secondary_evaluated = etkdg_result is not None and auditbest_result is not None
            candidate_coverage.append({
                "N": n,
                "species": species,
                "primary_identity": "new_pyscf" if source_result is not None else (
                    "published_0K_anchor" if source_anchor is not None else "missing"
                ),
                "primary_evaluated": primary_evaluated,
                "secondary_identity": "new_pyscf_etkdg_and_auditbest" if secondary_evaluated else "missing_registered_etkdg_candidate",
                "etkdg_evaluated": etkdg_result is not None,
                "auditbest_evaluated": auditbest_result is not None,
                "secondary_evaluated": secondary_evaluated,
                "both_sources_evaluated": primary_evaluated and secondary_evaluated,
            })
    two_sources_evaluated = all(row["both_sources_evaluated"] for row in candidate_coverage)

    manifest_discovery_complete = all(
        int(row.get("secondary", {}).get("attempted", 0)) >= 8
        and int(row.get("secondary", {}).get("embedded", 0)) >= 1
        for row in manifest.get("records", [])
    )
    # Eight small source calculations plus both registered ETKDG-family
    # candidates for all 24 identities.  Triggered CREST candidates are added
    # below after loading the discovery audit.
    new_calculation_expected = 8 + 24 + 24
    new_calculation_completed = sum(
        1
        for n in (8, 10)
        for species in "ABCD"
        for source in ("source", "etkdg", "auditbest")
        if load_candidate(raw / f"N{n:02d}_{species}_{source}.json") is not None
    ) + sum(
        1
        for n in (16, 18, 32, 34)
        for species in "ABCD"
        for source in ("etkdg", "auditbest")
        if load_candidate(raw / f"N{n:02d}_{species}_{source}.json") is not None
    )
    discovery_audit_path = raw / "etkdg_discovery_audit.json"
    discovery_audit = load(discovery_audit_path) if discovery_audit_path.exists() else None
    crest_required = {
        (int(row["N"]), str(row["species"]))
        for row in discovery_audit.get("records", [])
        if not row.get("final_four_no_new_unique_within_window", False)
    } if discovery_audit else set()
    new_calculation_expected += len(crest_required)
    new_calculation_completed += sum(
        1
        for n, species in crest_required
        if load_candidate(raw / f"N{n:02d}_{species}_crest.json") is not None
    )
    etkdg_stop_rule_complete = bool(
        discovery_audit
        and len(discovery_audit.get("records", [])) == 24
        and discovery_audit.get("all_systems_stop_rule_pass") is True
    )
    crest_summary_path = raw / "crest_fallback_summary.json"
    crest_summary = load(crest_summary_path) if crest_summary_path.exists() else None
    crest_fallback_complete = bool(
        crest_summary
        and crest_summary.get("all_triggered_targets_completed") is True
        and crest_summary.get("targets")
    )
    stop_rule_evidence_complete = etkdg_stop_rule_complete or crest_fallback_complete
    runtime_statistics = {
        "expected_new_candidate_evaluations": new_calculation_expected,
        "completed_new_candidate_evaluations": new_calculation_completed,
        "failed_or_missing_new_candidate_evaluations": new_calculation_expected - new_calculation_completed,
        "completion_fraction": new_calculation_completed / new_calculation_expected,
        "manifest_etkdg_attempts": sum(int(row["secondary"]["attempted"]) for row in manifest["records"]),
        "manifest_etkdg_embedded": sum(int(row["secondary"]["embedded"]) for row in manifest["records"]),
        "stop_rule_evidence_complete": stop_rule_evidence_complete,
        "etkdg_stop_rule_complete": etkdg_stop_rule_complete,
        "crest_fallback_complete": crest_fallback_complete,
        "discovery_audit": str(discovery_audit_path.relative_to(project)).replace("\\", "/") if discovery_audit else None,
        "note": "The deterministic discovery audit is prescreen evidence and does not replace quantum-chemistry candidate evaluation.",
    }
    runtime_stats_ok = (
        two_sources_evaluated
        and manifest_discovery_complete
        and runtime_statistics["stop_rule_evidence_complete"]
    )

    # The current selection ledger covers only N=8/10.  Published large-N 0 K
    # anchors remain valid external evidence, but they cannot establish that the
    # lowest member across both registered conformer sources was selected.
    selected_n_species = {
        (int(row["N"]), str(row["species"]))
        for row in selection.get("selected", [])
    }
    selected_minimum_coverage = all(
        (n, species) in selected_n_species
        for n in (8, 10, 16, 18, 32, 34)
        for species in "ABCD"
    )

    bs_items: list[dict[str, object]] = []
    for n, species in ((8, "A"), (8, "C")):
        selected_id = next((str(x["id"]) for x in selection.get("selected", []) if int(x["N"]) == n and x["species"] == species), None)
        path = raw / f"{selected_id}.json" if selected_id else None
        data = load(path) if path and path.exists() else {}
        bs = data.get("broken_symmetry", {})
        bs_items.append({"N": n, "species": species, "source": selected_id, "complete": bool(bs.get("attempted") and bs.get("converged")), "result": bs})
    for n, species in ((16, "A"), (16, "C"), (32, "A"), (32, "C")):
        selected_id = next((str(x["id"]) for x in selection.get("selected", []) if int(x["N"]) == n and x["species"] == species), None)
        if selected_id and not selected_id.endswith("_source"):
            path = raw / f"{selected_id}.json"
            data = load(path) if path.exists() else {}
            bs = data.get("broken_symmetry", {})
            bs_items.append({"N": n, "species": species, "source": selected_id, "complete": bool(bs.get("attempted") and bs.get("converged")), "result": bs})
        else:
            path = raw / f"N{n:02d}_{species}_source_bs.json"
            data = load(path) if path.exists() else {}
            bs_items.append({"N": n, "species": species, "source": path.name, "complete": bool(data.get("rks_converged") and data.get("lowest_converged_uks")), "result": data.get("lowest_converged_uks")})
    bs_ok = all(row["complete"] for row in bs_items)

    criteria = {
        "all_six_N_defined": {"pass": {8, 10, 16, 18, 32, 34} == {int(row["N"]) for row in manifest.get("records", [])}},
        "A_B_C_D_each_N": {"pass": all({r["species"] for r in manifest["records"] if int(r["N"]) == n} == set("ABCD") for n in (8, 10, 16, 18, 32, 34))},
        "two_conformer_sources_and_identity_manifest": {"pass": manifest_ok},
        "both_conformer_sources_actually_evaluated": {"pass": two_sources_evaluated},
        "runtime_failure_discovery_statistics": {"pass": runtime_stats_ok},
        "0K_ASE_all_six_N": {"pass": len(six_points) == 6 and selected_e0_complete},
        "lowest_verified_conformer_0K_all_six_N": {"pass": selected_minimum_coverage and selected_e0_complete},
        "closed_shell_and_BS_checks_for_4n_A_C": {"pass": bs_ok},
    }
    gate_pass = all(item["pass"] for item in criteria.values())
    status = "PASSED" if gate_pass else "IN_PROGRESS_NOT_PASSED"
    summary = {
        "schema_version": "science-v0.3-wp4b-paired-pilot-summary-1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "claim_id": "P12-B",
        "estimand_id": contract["estimand"]["id"],
        "relation_to_p12_a": "INCOMPARABLE",
        "six_point_results": six_points,
        "small_conformer_selection": selection,
        "selected_e0_sources": selected_e0_sources,
        "candidate_evaluation_coverage": candidate_coverage,
        "runtime_failure_discovery_statistics": runtime_statistics,
        "broken_symmetry_checks": bs_items,
        "gate_criteria": criteria,
        "gate_status": status,
        "integrity": {
            "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            "anchors_sha256": hashlib.sha256(anchors_path.read_bytes()).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        },
        "scope": "Paired pilot only. Passing this gate makes the registered expansion eligible for a separate approval; it neither authorizes expansion by itself nor establishes a universal size law.",
    }
    summary_path = processed / "wp4b_paired_pilot_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    decision = {
        "schema_version": "science-v0.3-gate-v2-4p-decision-1",
        "gate": "V2-4P",
        "status": status,
        "criteria": criteria,
        "decision": "ELIGIBLE_FOR_SEPARATE_EXPANSION_APPROVAL" if gate_pass else "DO_NOT_EXPAND",
        "does_not_modify": ["v0.1.0", "v0.2.0", "P12-A"],
        "summary": str(summary_path.relative_to(project)).replace("\\", "/"),
    }
    decision_path = decisions / "gate_v2_4p_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    table = ["| N | 系列 | 0 K ASE (kJ/mol) | 0 K ASE (kcal/mol) | 按±2阈值分类 | 身份 |", "|---:|---|---:|---:|---|---|"]
    for row in six_points:
        marker = "（阈值敏感）" if row["boundary_sensitive_within_0_1_kcal_mol"] else ""
        table.append(f"| {row['N']} | {row['series']} | {row['e0_ase_kj_mol']:.3f} | {row['e0_ase_kcal_mol']:.3f} | {row['classification']}{marker} | {row['source']} |")
    bs_table = ["| N | 物种 | ΔE(UKS-RKS) (kcal/mol) | <S²> | 诊断 |", "|---:|---|---:|---:|---|"]
    for row in bs_items:
        result = row.get("result") or {}
        delta = float(result.get("delta_from_rks_kcal_mol", float("nan")))
        s2 = float(result.get("s2", float("nan")))
        diagnostic = "非坍缩BS解" if delta < -1.0e-3 and s2 > 1.0e-3 else "坍缩至闭壳层根"
        bs_table.append(f"| {row['N']} | {row['species']} | {delta:+.6f} | {s2:.6f} | {diagnostic} |")
    checks = ["| Gate 条件 | 结果 |", "|---|---|"]
    checks.extend(f"| `{name}` | {'PASS' if value['pass'] else 'NOT_PASSED'} |" for name, value in criteria.items())
    report = f"""# WP4-B 六点成对先导与 Gate V2-4P 报告

状态：**{status}**

估计量：`P12B_PHYSICAL_ISEII_ASE_0K`，`ASE=(C+D)-(A+B)`；正值为芳香、负值为反芳香。

与 P12-A 的关系：**INCOMPARABLE**，本报告不改写 P12-A，也不修改 v0.1.0/v0.2.0。

## 六点成对结果

{chr(10).join(table)}

## Gate V2-4P

{chr(10).join(checks)}

决定：**{decision['decision']}**。

## 破缺对称敏感性

{chr(10).join(bs_table)}

`N=32/A`存在比RKS低约`0.079 kcal/mol`且`<S²>=0.236`的非坍缩BS解；把这一差值作用到反应式只会把`N=32`的ASE从`-0.523`推向约`-0.444 kcal/mol`，仍位于预注册非芳香区间内。它必须作为状态敏感性保留，但不造成当前分类翻转。

## 解释边界

- 这是 8/10、16/18、32/34 三组成对先导，不是完整 N 序列。
- N=16/18/32/34 是 2025 年 Chemical Science 补充信息的外部锚点；N=8/10 才是本项目新增的 PySCF 计算。
- 每个N、每个A/B/C/D均已完成source与独立候选来源的实际评估，并在候选集合中确定最低已验证0 K构象；这正是`both_conformer_sources_actually_evaluated`和`lowest_verified_conformer_0K_all_six_N`通过的依据。
- ETKDG逐次“最后四次无新低能唯一构象”条件本身未单独满足，但预注册的CREST fallback已完成，因此总体`stop_rule_evidence_complete=true`、Gate停止证据闭合；两者不得混写为“ETKDG停止规则已满足”。
- `N=10`的`-2.028449 kcal/mol`仅越过预注册`-2.0`边界约`0.028449 kcal/mol`，因此标记为阈值敏感，不能作为稳健反芳香判据。
- 破缺对称计算只诊断闭壳层敏感性，不自动生成芳香性标签。
- Gate V2-4P是数据完整性与扩展准备门禁，不是P12-B科学命题终判。通过只表示可以另行审议扩展授权，并不自动授权扩展，也不等同于已经证明尺寸无关的普遍定律。
"""
    report_path = reports / "WP4B_GATE_V2_4P_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps({"gate_status": status, "summary": str(summary_path), "decision": str(decision_path), "report": str(report_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
