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
    "P11/substituent-result.json": "P11B_CONJUGATIVE_CONSISTENT_INDUCTIVE_INCONSISTENT_UNDER_SOURCE_PROXY",
    "P12/result.json": "P12_PARTIALLY_CONSISTENT_QUALITATIVE_BOUNDARY_CONSISTENT_EXACT_ONSET_CROSS_ESTIMATOR_INCONSISTENT",
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

    p14 = load_json("P14/result.json")
    if p14.get("classification") != "consistent" or p14.get("decision_verdict") != "PASS":
        failures.append("P14/result.json: frozen classification or decision verdict changed")

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
