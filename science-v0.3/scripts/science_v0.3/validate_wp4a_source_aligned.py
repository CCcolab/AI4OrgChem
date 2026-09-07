from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    contract = load(ROOT / "configs/science_v0.3/wp4a_source_aligned_contract.json")
    evidence = load(ROOT / contract["source_evidence"])
    decision = load(ROOT / "data/science_v0.3/decisions/wp4a/gate_v2_4a_decision.json")
    assert contract["estimand"]["relation_to_v0_1_p12"] == "SAME_ESTIMAND"
    assert contract["estimand"]["relation_to_wp4b"] == "INCOMPARABLE"
    assert [int(row["N"]) for row in evidence["rows"]] == contract["required_N"]
    assert all(evidence["acceptance_checks"].values())
    assert evidence["source_internal_verdict"] == "SOURCE_TABLES_SUPPORT_N16_N18_BOUNDARY_LOGIC"
    assert evidence["historical_quantum_program_reproduced"] is False
    assert decision["status"] == "CLOSED_SOURCE_ALIGNED_R1"
    assert decision["evidence_level"] == "R1"
    assert decision["checks"]["six_source_rows_present"] is True
    assert decision["checks"]["printed_precision_energy_identities_close"] is True
    assert decision["checks"]["source_internal_boundary_logic_supported"] is True
    assert decision["checks"]["historical_quantum_program_reproduced"] is False
    assert decision["checks"]["independent_physical_state_claimed"] is False
    print("WP4A_SOURCE_ALIGNED_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
