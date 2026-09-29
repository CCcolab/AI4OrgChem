from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P12 = ROOT / "evidence" / "P01-P14" / "P12"


def load(name: str) -> dict:
    return json.loads((P12 / name).read_text(encoding="utf-8"))


def digest(name: str) -> str:
    return hashlib.sha256((P12 / name).read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    result = load("result.json")
    if result.get("verdict") != "P12_CONSISTENT":
        failures.append("P12 verdict is not P12_CONSISTENT")
    if result.get("validation_result") != "PASS_P12_CONSISTENT":
        failures.append("P12 validation result changed")
    if result.get("classification") != "consistent":
        failures.append("P12 classification changed")
    if result.get("original_program_code_used") is not False:
        failures.append("original-program-code boundary changed")
    if result.get("exact_numeric_reproduction_claimed") is not False:
        failures.append("exact-numeric-reproduction boundary changed")

    points = {row["N"]: row for row in result.get("evidence_points", [])}
    if set(points) != {12, 14, 16}:
        failures.append("P12 evidence point set must be N12/N14/N16")
    expected = {
        12: (13.237141505979704, 1.853186530126255, 2.887010155434692),
        14: (-6.366235934598773, -16.92839471470879, -15.947079304828947),
        16: (15.804323365228473, -1.6223407473112494, -0.33952721462311064),
    }
    for n, values in expected.items():
        row = points.get(n, {})
        actual = (row.get("delta_EA_kcal_mol"), row.get("ESE_kcal_mol"), row.get("CESE_kcal_mol"))
        if any(a is None or abs(a - b) > 1.0e-9 for a, b in zip(actual, values)):
            failures.append(f"N{n} registered values changed")
        ledger_name = row.get("ledger", "")
        if not ledger_name or not (P12 / ledger_name).is_file():
            failures.append(f"N{n} ledger missing")
            continue
        if row.get("ledger_sha256") != digest(ledger_name):
            failures.append(f"N{n} ledger hash mismatch")
        ledger = load(ledger_name)
        values_record = ledger.get("ledger", {})
        for key, expected_value in zip(("delta_EA_kcal_mol", "ESE_kcal_mol", "CESE_kcal_mol"), values):
            if abs(values_record.get(key, 1e99) - expected_value) > 1.0e-9:
                failures.append(f"N{n} ledger {key} changed")

    n16 = points.get(16, {})
    n16_ledger = load("n16-same-basis-ledger.json")
    if n16.get("direct_GE_count") != 28 or n16.get("symmetry_weighting_used") is not False:
        failures.append("N16 result coverage changed")
    if len(n16_ledger.get("pair_rows", [])) != 28:
        failures.append("N16 ledger must contain 28 direct GE rows")
    if abs(n16.get("relative_CESE", 1.0) - 0.021031365035480403) > 1.0e-12:
        failures.append("N16 relative CESE changed")
    if n16.get("relative_CESE", 1.0) > n16.get("relative_CESE_maximum", 0.0):
        failures.append("N16 relative CESE threshold failed")
    if result.get("all_registered_checks_pass") is not True:
        failures.append("registered P12 checks are not all passing")
    if result.get("same_estimand_opposition_established") is not False:
        failures.append("same-estimand opposition boundary changed")

    historical = load("result-v0.3.1-historical.json")
    historical_verdict = historical.get("verdict") or historical.get("scientific_verdict")
    if historical_verdict != "P12_PARTIALLY_CONSISTENT_QUALITATIVE_BOUNDARY_CONSISTENT_EXACT_ONSET_NOT_DIRECTLY_COMPARABLE":
        failures.append("historical v0.3.1 P12 result changed")

    output = {
        "status": "PASS" if not failures else "FAIL",
        "verdict": result.get("verdict"),
        "evidence_points": sorted(points),
        "n16_direct_GE_count": len(n16_ledger.get("pair_rows", [])),
        "failures": failures,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
