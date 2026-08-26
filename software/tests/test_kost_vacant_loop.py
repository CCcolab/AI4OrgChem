from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.kost import occupied_then_vacant_kost


class KostVacantLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metric = np.eye(7)
        self.target = np.eye(7)[:, 0]
        self.occupied = np.eye(7)[:, 1:3]
        self.vacant = np.eye(7)[:, 3:6]
        self.probe = np.array([0.2, -0.3, 0.4, 0.5, -0.6, 0.1, 1.0])

    def run_loop(self, **options: object) -> dict[str, object]:
        return occupied_then_vacant_kost(
            self.target,
            self.occupied,
            self.vacant,
            self.probe,
            self.metric,
            occupied_labels=[10, 11],
            vacant_labels=[20, 21, 22],
            **options,
        )

    def test_one_vacant_sweep_cancels_vacants_and_reconstructs(self) -> None:
        result = self.run_loop()
        self.assertTrue(result["occupied_result"]["converged"])
        self.assertTrue(result["vacant_converged"])
        self.assertEqual(result["vacant_sweeps_completed"], 1)
        self.assertEqual(result["vacant_rotation_count"], 3)
        self.assertLess(result["maximum_vacant_off_target_overlap"], 1.0e-14)
        self.assertLess(result["full_target_maximum_residual"], 1.0e-14)
        self.assertLess(result["reconstruction_residual"], 1.0e-14)
        self.assertLess(result["cumulative_orthogonality_residual"], 1.0e-14)
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)

    def test_vacant_sweep_measures_but_does_not_repair_occupied_feedback(self) -> None:
        result = self.run_loop()
        self.assertFalse(result["occupied_probe_reintroduced_above_tolerance"])
        self.assertLess(result["occupied_probe_feedback_maximum_change"], 1.0e-14)
        self.assertLess(result["occupied_coefficient_feedback_residual"], 1.0e-14)
        self.assertLess(result["target_occupied_metric_feedback_maximum_change"], 1.0e-14)

    def test_nonorthogonal_metric_exposes_target_occupied_feedback(self) -> None:
        metric = np.eye(7)
        metric[1, 3] = metric[3, 1] = 0.2
        result = occupied_then_vacant_kost(
            self.target,
            self.occupied,
            self.vacant,
            self.probe,
            metric,
            occupied_labels=[10, 11],
            vacant_labels=[20, 21, 22],
        )
        self.assertTrue(result["vacant_converged"])
        self.assertGreater(
            result["target_occupied_metric_feedback_maximum_change"], 1.0e-3
        )
        self.assertLess(result["occupied_probe_feedback_maximum_change"], 1.0e-14)
        self.assertLess(result["occupied_coefficient_feedback_residual"], 1.0e-14)

    def test_vacant_permutation_preserves_final_target_projector(self) -> None:
        reference = self.run_loop()
        permutation = [2, 0, 1]
        changed = occupied_then_vacant_kost(
            self.target,
            self.occupied,
            self.vacant[:, permutation],
            self.probe,
            self.metric,
            occupied_labels=[10, 11],
            vacant_labels=[22, 20, 21],
        )
        reference_target = reference["current_block"][:, [0]]
        changed_target = changed["current_block"][:, [0]]
        np.testing.assert_allclose(
            reference_target @ reference_target.T,
            changed_target @ changed_target.T,
            atol=1.0e-14,
        )

    def test_phase_flips_preserve_subspace_observables(self) -> None:
        reference = self.run_loop()
        changed = occupied_then_vacant_kost(
            -self.target,
            self.occupied * np.array([-1.0, 1.0]),
            self.vacant * np.array([1.0, -1.0, 1.0]),
            -self.probe,
            self.metric,
            occupied_labels=[10, 11],
            vacant_labels=[20, 21, 22],
        )
        self.assertAlmostEqual(
            reference["final_target_magnitude"], changed["final_target_magnitude"]
        )
        np.testing.assert_allclose(
            np.linalg.eigvalsh(reference["current_gram"]),
            np.linalg.eigvalsh(changed["current_gram"]),
            atol=1.0e-14,
        )

    def test_zero_vacant_sweep_retains_failure(self) -> None:
        result = self.run_loop(vacant_sweeps=0)
        self.assertFalse(result["vacant_converged"])
        self.assertEqual(result["vacant_sweeps_completed"], 0)
        self.assertEqual(result["vacant_rotation_count"], 0)
        self.assertEqual(result["vacant_history"], [])
        self.assertGreater(result["maximum_vacant_off_target_overlap"], 1.0e-10)

    def test_more_than_one_vacant_sweep_is_out_of_scope(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero or one"):
            self.run_loop(vacant_sweeps=2)


if __name__ == "__main__":
    unittest.main()
