from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class V02ReleaseContractTests(unittest.TestCase):
    def test_completed_scientific_lanes_are_not_overstated(self) -> None:
        wp1 = load("data/science_v0.2/decisions/wp1/gate_v2_1_decision.json")
        wp2 = load("data/science_v0.2/decisions/wp2/gate_v2_2_decision.json")
        wp3 = load("data/science_v0.2/decisions/wp3/gate_v2_3_decision.json")
        wp4 = load("data/science_v0.2/decisions/wp4/gate_v2_4p_decision.json")
        self.assertEqual("PASS_WITH_METHOD_SENSITIVITY", wp1["gate_status"])
        self.assertEqual("PARTIALLY_SUPPORTED", wp1["conclusion_state"])
        self.assertEqual("FAIL", wp2["open_program_lane"])
        self.assertEqual("FAIL", wp2["psi4_backend_contract"])
        self.assertFalse(wp2["orca_available"])
        self.assertEqual("NOT_PASSED", wp2["gate_status"])
        self.assertEqual("PASS", wp3["gate_status"])
        self.assertEqual("R3", wp3["p10b_grade"])
        self.assertEqual("NOT_PASSED", wp4["gate_status"])
        self.assertFalse(wp4["scientific_calculation_started"])
        self.assertFalse(wp4["v0_1_p12_a_changed"])

    def test_agent_replay_axis_is_separate(self) -> None:
        replay = load("runs/science_v0.2/wp5_internal_clean_replay/replay_result.json")
        self.assertTrue(replay["pass"])
        self.assertEqual("INTERNAL_CLEAN_REPLAY", replay["replay_status"])
        self.assertEqual("M1_PLUS", replay["agent_maturity"])
        self.assertFalse(replay["external_replayer"])
        self.assertFalse(replay["scientific_calculations_rerun"])

    def test_v0_1_baseline_is_immutable(self) -> None:
        baseline = load("configs/science_v0.2/v0.1_baseline.json")
        self.assertTrue(baseline["contract"]["read_only"])
        self.assertFalse(baseline["contract"]["v0.2_may_overwrite_v0.1"])


if __name__ == "__main__":
    unittest.main()
