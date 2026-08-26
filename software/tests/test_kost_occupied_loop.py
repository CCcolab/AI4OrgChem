from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.kost import occupied_kost_loop


class KostOccupiedLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metric = np.eye(5)
        self.target = np.eye(5)[:, 0]
        self.auxiliaries = np.eye(5)[:, 1:4]
        self.probe = np.array([0.2, -0.3, 0.4, 0.5, 1.0])

    def test_sweep_cancels_all_auxiliaries_and_reconstructs(self) -> None:
        result = occupied_kost_loop(
            self.target,
            self.auxiliaries,
            self.probe,
            self.metric,
            auxiliary_labels=[10, 11, 12],
        )
        self.assertTrue(result["converged"])
        self.assertEqual(result["sweeps_completed"], 1)
        self.assertEqual(result["rotation_count"], 3)
        self.assertLess(result["maximum_off_target_overlap"], 1.0e-14)
        self.assertLess(result["target_maximum_residual"], 1.0e-14)
        self.assertLess(result["reconstruction_residual"], 1.0e-14)
        self.assertLess(result["cumulative_orthogonality_residual"], 1.0e-14)
        self.assertGreaterEqual(result["monotonic_minimum_increment"], -1.0e-14)

    def test_nonidentity_metric_covariance(self) -> None:
        metric = np.eye(5)
        metric[0, 1] = metric[1, 0] = 0.1
        metric[2, 3] = metric[3, 2] = -0.2
        result = occupied_kost_loop(
            self.target, self.auxiliaries, self.probe, metric
        )
        self.assertTrue(result["converged"])
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)

    def test_auxiliary_permutation_preserves_final_target_projector(self) -> None:
        reference = occupied_kost_loop(
            self.target, self.auxiliaries, self.probe, self.metric
        )
        permutation = [2, 0, 1]
        permuted = occupied_kost_loop(
            self.target,
            self.auxiliaries[:, permutation],
            self.probe,
            self.metric,
            auxiliary_labels=permutation,
        )
        reference_target = reference["current_block"][:, [0]]
        permuted_target = permuted["current_block"][:, [0]]
        reference_projector = reference_target @ reference_target.T
        permuted_projector = permuted_target @ permuted_target.T
        np.testing.assert_allclose(reference_projector, permuted_projector, atol=1.0e-14)
        self.assertAlmostEqual(
            reference["final_target_magnitude"], permuted["final_target_magnitude"]
        )

    def test_input_phase_flips_preserve_final_observables(self) -> None:
        reference = occupied_kost_loop(
            self.target, self.auxiliaries, self.probe, self.metric
        )
        signs = np.array([-1.0, 1.0, -1.0])
        changed = occupied_kost_loop(
            -self.target,
            self.auxiliaries * signs,
            -self.probe,
            self.metric,
        )
        self.assertAlmostEqual(
            reference["final_target_magnitude"], changed["final_target_magnitude"]
        )
        np.testing.assert_allclose(
            np.linalg.eigvalsh(reference["current_gram"]),
            np.linalg.eigvalsh(changed["current_gram"]),
            atol=1.0e-14,
        )

    def test_insufficient_cap_is_retained_as_nonconverged(self) -> None:
        result = occupied_kost_loop(
            self.target,
            self.auxiliaries,
            self.probe,
            self.metric,
            maximum_sweeps=0,
        )
        self.assertFalse(result["converged"])
        self.assertEqual(result["sweeps_completed"], 0)
        self.assertEqual(result["rotation_count"], 0)
        self.assertEqual(result["history"], [])
        self.assertGreater(result["maximum_off_target_overlap"], 1.0e-10)


if __name__ == "__main__":
    unittest.main()
