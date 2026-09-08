"""Validate the self-contained P01-P14 public evidence package.

This validator intentionally uses only files shipped in ``publication``.  It
does not require the private development tree, the monograph, or raw quantum-
chemistry outputs.
"""

from __future__ import annotations

import json
from pathlib import Path


PUBLICATION = Path(__file__).resolve().parents[2]
EVIDENCE = PUBLICATION / "evidence" / "P01-P14"


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


def load_json(relative: str) -> dict:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def load_jsonl(relative: str) -> list[dict]:
    return [json.loads(line) for line in (EVIDENCE / relative).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    failures: list[str] = []
    for number in range(1, 15):
        directory = EVIDENCE / f"P{number:02d}"
        if not directory.is_dir():
            failures.append(f"missing proposition directory P{number:02d}")
        elif not any(directory.glob("*result.json*")):
            failures.append(f"missing machine result for P{number:02d}")

    for relative, expected in EXPECTED_JSON_VERDICTS.items():
        record = load_json(relative)
        actual = record.get("verdict") or record.get("scientific_verdict")
        if actual != expected:
            failures.append(f"{relative}: expected verdict {expected!r}, got {actual!r}")

    p03 = load_json("P03/result.json")
    if p03.get("proposition_id") != "P03" or len(p03.get("points", [])) < 2:
        failures.append("P03/result.json lacks the frozen P03 point series")

    for relative in ("P04/result.jsonl", "P05/result.jsonl", "P06/result.jsonl"):
        rows = load_jsonl(relative)
        if not rows or any("final_scoped_label" not in row for row in rows):
            failures.append(f"{relative}: missing scoped labels")

    p05 = load_json("P05/seven-angle-result.json")
    p05_expected_angles = {"0.0", "5.0", "10.0", "17.0", "25.0", "35.0", "45.0"}
    if (
        p05.get("decision_verdict") != "PASS_P05_SEVEN_ANGLE_CONTINUATION"
        or p05.get("scientific_verdict") != "P05_CONSISTENT_WITH_MULTI_ANGLE_SUPPORT"
        or set(p05.get("points", {})) != p05_expected_angles
        or not all(p05.get("checks", {}).values())
        or any(p05.get("angle_labels", {}).get(angle) != "destabilizing" for angle in p05_expected_angles - {"0.0"})
        or p05.get("angle_labels", {}).get("0.0") != "indeterminate"
    ):
        failures.append("P05/seven-angle-result.json: completed continuation evidence changed")

    p07_audit = load_json("P07/same-hamiltonian-audit-result.json")
    if (
        p07_audit.get("verdict") != "P07_CONSISTENT_WITH_INDEPENDENT_SAME_HAMILTONIAN_PATH_AUDIT"
        or p07_audit.get("evidence_identity") != "INDEPENDENT_COMPUTATIONAL_AUDIT_PLUS_DERIVED_SYNTHESIS"
        or p07_audit.get("technical_pass") is not True
        or set(p07_audit.get("points", {})) != {"0.0", "17.0"}
        or any(
            abs(point["naive_three_terms_hartree"]["closure_residual_vs_E_G_minus_E_FUL"]) < 0.30
            for point in p07_audit.get("points", {}).values()
        )
        or any(
            abs(point["path_complete_three_terms_hartree"]["closure_residual_vs_E_G_minus_E_FUL"]) > 1.0e-9
            for point in p07_audit.get("points", {}).values()
        )
    ):
        failures.append("P07/same-hamiltonian-audit-result.json: independent path audit changed")

    p14 = load_json("P14/result.json")
    if p14.get("classification") != "consistent" or p14.get("decision_verdict") != "PASS":
        failures.append("P14/result.json: frozen classification or decision verdict changed")

    p11 = load_json("P11/substituent-result.json")
    if (
        p11.get("classification") != "consistent"
        or len(p11.get("state_energies_hartree", {})) != 13
        or not all(p11.get("acceptance_checks", {}).values())
    ):
        failures.append("P11/substituent-result.json: source-2007 planar ledger is incomplete")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "propositions_checked": 14,
        "failures": failures,
        "scope": "packaged processed evidence and frozen verdict integrity only",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
