from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.kost import bounded_alternating_kost


class KostBoundedAlternationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metric = np.eye(7)
        self.target = np.eye(7)[:, 0]
        self.occupied = np.eye(7)[:, 1:3]
        self.vacant = np.eye(7)[:, 3:6]
        self.probe = np.array([0.2, -0.3, 0.4, 0.5, -0.6, 0.1, 1.0])

    def run_loop(self, metric: np.ndarray | None = None, **options: object) -> dict[str, object]:
        return bounded_alternating_kost(
            self.target,
            self.occupied,
            self.vacant,
            self.probe,
            self.metric if metric is None else metric,
            occupied_labels=[10, 11],
            vacant_labels=[20, 21, 22],
            **options,
        )

    def test_orthogonal_case_stops_after_first_cycle(self) -> None:
        result = self.run_loop()
        self.assertTrue(result["converged"])
        self.assertTrue(result["scheduler_quiescent"])
        self.assertFalse(result["joint_physical_convergence_claimed"])
        self.assertFalse(result["cap_exhausted"])
        self.assertEqual(result["cycles_completed"], 1)
        self.assertEqual(result["return_edge_count"], 0)
        self.assertFalse(result["history"][0]["return_required"])
        self.assertLess(result["maximum_occupied_probe_overlap"], 1.0e-14)
        self.assertLess(result["maximum_vacant_probe_overlap"], 1.0e-14)

    def test_nonorthogonal_positive_control_takes_return_edge(self) -> None:
        metric = np.eye(7)
        metric[1, 3] = metric[3, 1] = 0.2
        result = self.run_loop(metric=metric)
        self.assertTrue(result["converged"])
        self.assertTrue(result["scheduler_quiescent"])
        self.assertFalse(result["joint_physical_convergence_claimed"])
        self.assertEqual(result["cycles_completed"], 2)
        self.assertEqual(result["return_edge_count"], 1)
        self.assertTrue(result["history"][0]["return_required"])
        self.assertFalse(result["history"][1]["return_required"])
        self.assertGreater(result["history"][0]["target_occupied_feedback"], 1.0e-3)

    def test_positive_control_cap_exhaustion_is_retained(self) -> None:
        metric = np.eye(7)
        metric[1, 3] = metric[3, 1] = 0.2
        result = self.run_loop(metric=metric, maximum_cycles=1)
        self.assertFalse(result["converged"])
        self.assertTrue(result["cap_exhausted"])
        self.assertEqual(result["cycles_completed"], 1)
        self.assertEqual(result["return_edge_count"], 0)
        self.assertTrue(result["history"][0]["return_required"])

    def test_zero_cycle_cap_retains_unprocessed_state(self) -> None:
        result = self.run_loop(maximum_cycles=0)
        self.assertFalse(result["converged"])
        self.assertTrue(result["cap_exhausted"])
        self.assertEqual(result["cycles_completed"], 0)
        self.assertEqual(result["history"], [])
        np.testing.assert_allclose(result["current_block"], result["initial_block"])

    def test_full_cumulative_transform_reconstructs_across_return(self) -> None:
        metric = np.eye(7)
        metric[1, 3] = metric[3, 1] = 0.2
        result = self.run_loop(metric=metric)
        self.assertLess(result["reconstruction_residual"], 1.0e-14)
        self.assertLess(result["cumulative_orthogonality_residual"], 1.0e-14)
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)

    def test_phase_and_within_block_permutations_preserve_path(self) -> None:
        reference = self.run_loop()
        changed = bounded_alternating_kost(
            -self.target,
            self.occupied[:, [1, 0]] * np.array([-1.0, 1.0]),
            self.vacant[:, [2, 0, 1]] * np.array([1.0, -1.0, 1.0]),
            -self.probe,
            self.metric,
            occupied_labels=[11, 10],
            vacant_labels=[22, 20, 21],
        )
        self.assertEqual(reference["cycles_completed"], changed["cycles_completed"])
        self.assertEqual(reference["return_edge_count"], changed["return_edge_count"])
        self.assertAlmostEqual(
            reference["final_target_magnitude"], changed["final_target_magnitude"]
        )


if __name__ == "__main__":
    unittest.main()
