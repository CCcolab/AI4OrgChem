"""Validate the bilingual P01-P14 evidence navigation against packaged results."""

from __future__ import annotations

import json
import re
from pathlib import Path


PUBLICATION = Path(__file__).resolve().parents[2]
EVIDENCE = PUBLICATION / "evidence" / "P01-P14"

EXPECTED_CLASS = {
    "P01": "consistent",
    "P02": "consistent",
    "P03": "consistent",
    "P04": "consistent",
    "P05": "scope-consistent",
    "P06": "consistent",
    "P07": "scope-consistent",
    "P08": "consistent",
    "P09": "consistent",
    "P10": "consistent",
    "P11": "consistent",
    "P12": "partially-consistent",
    "P13": "consistent",
    "P14": "consistent",
}

EXPECTED_JSON_VERDICTS = {
    "P01/result.json": "P01_SCOPED_CONCEPTUAL_DISTINCTION_SUPPORTED",
    "P02/result.json": "P02_PUBLISHED_DATA_SCOPED_PROPOSITION_SUPPORTED",
    "P07/result.json": "P07_SCOPED_MULTI_COMPONENT_MECHANISM_SUPPORTED_WITHOUT_CROSS_PROTOCOL_ENERGY_SUM",
    "P08/result.json": "P08_SCOPED_BUTADIENE_PROPOSITION_SUPPORTED",
    "P09/result.json": "P09_SCOPED_PROPOSITION_SUPPORTED",
    "P10/result.json": "P10_SCOPED_PROPOSITION_SUPPORTED",
    "P11/furan-result.json": "P11A_SCOPED_FURAN_LDE_SUPPORTED",
    "P11/substituent-result.json": "P11B_SOURCE2007_PLANAR_RECALCULATION_CONSISTENT",
    "P12/result.json": "P12_PARTIALLY_CONSISTENT_QUALITATIVE_BOUNDARY_CONSISTENT_EXACT_ONSET_NOT_DIRECTLY_COMPARABLE",
    "P13/result.json": "P13_CONSISTENT_IN_TESTED_RULE_HIERARCHY_AND_PUBLISHED_LEDGER_SCOPE",
}

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ROW = re.compile(r"^\| (P\d{2}) \|.*$", re.MULTILINE)

AUTHORITATIVE_STATUS_REQUIREMENTS = {
    "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md": ("thirteen are consistent", "P05 and P07", "one (P12) is partially consistent"),
    "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md": ("13项一致", "P05、P07", "1项（P12）部分一致"),
    "README.md": ("13 consistent with the corresponding monograph proposition within their declared tested domains", "P05 and P07", "1 partially consistent", "P12"),
    "README_zh-CN.md": ("13项一致", "P05、P07", "受测范围内一致", "1项部分一致", "P12"),
    "project/ACHIEVEMENTS_zh-CN.md": ("十三项与原著一致", "P05、P07", "P12仍为部分一致"),
    "project/P01-P14_MASTER_TABLE_zh-CN.md": ("P11", "CE=+1.173122", "IE=+0.490079", "一致4项"),
    "manuscripts/P01-P14_evidence_matrix_zh-CN.md": ("一致13项", "P05、P07为受测范围内一致", "部分一致1项（P12）", "IE=+0.490079"),
    "manuscripts/PUBLICATION_POSITIONING_EN.md": ("Thirteen are consistent with the monograph within their declared tested domains", "P05 and P07", "one (P12) is partially consistent"),
    "manuscripts/PUBLICATION_POSITIONING_zh-CN.md": ("十三项一致", "P05、P07", "一项（P12）部分一致"),
    "ai4s-agent/CAPABILITIES_AND_RESULTS_zh-CN.md": ("十三项一致", "P05、P07", "一项部分一致（P12）"),
}

FORBIDDEN_CURRENT_FRAGMENTS = (
    "12 consistent or scope-consistent",
    "2 partially consistent",
    "十二项一致或范围化一致",
    "两项部分一致",
    "P11、P12 为部分一致",
    "P11B_CONJUGATIVE_CONSISTENT_INDUCTIVE_INCONSISTENT_UNDER_SOURCE_PROXY",
    "**范围化一致**",
    "**Scope-consistent**",
)


def load_json(relative: str) -> dict:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    indexes = {
        "en": EVIDENCE / "README.md",
        "zh": EVIDENCE / "README_zh-CN.md",
    }
    expected_ids = set(EXPECTED_CLASS)
    link_count = 0

    for language, path in indexes.items():
        if not path.is_file():
            failures.append(f"missing {language} evidence index")
            continue
        text = path.read_text(encoding="utf-8")
        rows = ROW.findall(text)
        if len(rows) != 14 or set(rows) != expected_ids:
            failures.append(f"{language} index does not contain exactly one row for P01-P14")
        for target in LINK.findall(text):
            clean = target.split("#", 1)[0]
            if clean.startswith(("http://", "https://")):
                continue
            link_count += 1
            if not (path.parent / clean).resolve().exists():
                failures.append(f"broken {language} evidence link: {target}")

        required_fragments = {
            "P11": ["+1.173122", "+1.2", "+0.490079", "+0.49", "13/13"],
            "P12": ["N=16/18", "N>30"],
        }
        for proposition, fragments in required_fragments.items():
            if any(fragment not in text for fragment in fragments):
                failures.append(f"{language} index lacks required {proposition} difference values")

    if link_count < 120:
        failures.append(f"only {link_count} navigation links found; expected at least 120")

    for relative, expected in EXPECTED_JSON_VERDICTS.items():
        record = load_json(relative)
        actual = record.get("verdict") or record.get("scientific_verdict")
        if actual != expected:
            failures.append(f"machine verdict changed: {relative}")

    p03 = load_json("P03/result.json")
    if p03.get("proposition_id") != "P03":
        failures.append("P03 machine result identity changed")
    p14 = load_json("P14/result.json")
    if p14.get("classification") != "consistent" or p14.get("decision_verdict") != "PASS":
        failures.append("P14 machine classification changed")

    for relative, expected_label in {
        "P04/result.jsonl": "pi_conjugation_endpoint_destabilizing_in_tested_source_proxy_domain",
        "P06/result.jsonl": "nonbonded_sigma_sigma_source_endpoint_destabilizing_at_both_table_5_19_source_proxy_points",
    }.items():
        rows = [
            json.loads(line)
            for line in (EVIDENCE / relative).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if expected_label not in {row.get("final_scoped_label") for row in rows}:
            failures.append(f"machine scoped label changed: {relative}")

    p05_rows = [
        json.loads(line)
        for line in (EVIDENCE / "P05/result.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    p05_labels = {row.get("final_scoped_label") for row in p05_rows}
    if not {
        "indeterminate_within_tolerance",
        "pi_sigma_source_endpoint_destabilizing_at_17deg_table_5_15_source_proxy",
    }.issubset(p05_labels):
        failures.append("P05 scoped/indeterminate labels changed")

    for relative, required in AUTHORITATIVE_STATUS_REQUIREMENTS.items():
        path = PUBLICATION / relative
        if not path.is_file():
            failures.append(f"missing authoritative current-status document: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for fragment in required:
            if fragment not in text:
                failures.append(f"{relative}: missing current-status fragment {fragment!r}")
        for fragment in FORBIDDEN_CURRENT_FRAGMENTS:
            if fragment in text:
                failures.append(f"{relative}: stale current-status fragment {fragment!r}")

    agent_summary = json.loads((PUBLICATION / "ai4s-agent" / "EVALUATION_SUMMARY.json").read_text(encoding="utf-8"))
    counts = agent_summary.get("scientific_propositions", {})
    expected_count_fields = {
        "total": 14,
        "consistent_or_scope_consistent": 13,
        "scope_qualified_consistent": 2,
        "scope_qualified_consistent_ids": ["P05", "P07"],
        "partially_consistent": 1,
        "globally_inconsistent": 0,
    }
    if any(counts.get(key) != value for key, value in expected_count_fields.items()):
        failures.append("AI4S Agent machine-readable proposition counts are not the current 13+1 state")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "propositions_navigated": 14,
        "bilingual_indexes": 2,
        "navigation_links_checked": link_count,
        "classification_counts": {
            "consistent_or_scope_consistent": 13,
            "partially_consistent": 1,
            "globally_inconsistent": 0,
            "unknown": 0,
        },
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
