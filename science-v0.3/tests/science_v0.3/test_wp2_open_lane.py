from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


class WP2OpenThreeProgramContractTest(unittest.TestCase):
    def test_gate_and_summary_are_consistent(self) -> None:
        decision = load(
            "data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json"
        )
        summary = load(
            "data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json"
        )
        self.assertEqual(decision["status"], "PASSED_OPEN_THREE_PROGRAM")
        self.assertTrue(summary["open_three_program_lane_pass"])
        self.assertEqual(summary["anchor_count"], 8)
        self.assertTrue(all(row["pass"] for row in summary["anchors"]))
        self.assertTrue(all(row["pass"] for row in summary["relative_energy_pairs"]))
        self.assertEqual(decision["summary_sha256"], sha256(decision["summary"]))

    def test_published_anchor_hashes_match(self) -> None:
        summary = load(
            "data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json"
        )
        for row in summary["anchors"]:
            self.assertEqual(row["result_sha256"], sha256(row["result"]))
            record = load(row["result"])
            self.assertEqual(len(record["programs"]), 3)
            self.assertTrue(record["comparison"]["pass"])

    def test_scope_boundaries_are_explicit(self) -> None:
        decision = load(
            "data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json"
        )
        self.assertEqual(
            decision["original_orca_lane_status"],
            "NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE",
        )
        self.assertTrue(
            decision["effect_on_v0_1_fourteen_propositions"].startswith("NO_CHANGE")
        )
        self.assertTrue(decision["effect_on_v0_2_release"].startswith("NO_MUTATION"))


if __name__ == "__main__":
    unittest.main()
