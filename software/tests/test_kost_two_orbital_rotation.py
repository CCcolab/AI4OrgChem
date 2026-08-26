from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.kost import rotate_to_fixed_probe


class KostTwoOrbitalRotationTests(unittest.TestCase):
    def test_exact_cancellation_and_maximum_on_orthonormal_example(self) -> None:
        metric = np.eye(3)
        target = np.array([1.0, 0.0, 0.0])
        auxiliary = np.array([0.0, 1.0, 0.0])
        probe = np.array([0.6, -0.8, 0.0])
        result = rotate_to_fixed_probe(target, auxiliary, probe, metric)
        self.assertLess(result["off_target_overlap_residual"], 1.0e-14)
        self.assertAlmostEqual(result["achieved_target_overlap"], 1.0)
        self.assertLess(result["target_maximum_residual"], 1.0e-14)
        self.assertLess(result["reconstruction_residual"], 1.0e-14)

    def test_nonidentity_metric_preserves_covariant_gram(self) -> None:
        metric = np.array([[1.0, 0.2, 0.1], [0.2, 1.3, -0.1], [0.1, -0.1, 0.9]])
        target = np.array([1.0, 0.0, 0.0])
        auxiliary = np.array([0.0, 1.0, 0.0])
        probe = np.array([0.2, -0.3, 1.0])
        result = rotate_to_fixed_probe(target, auxiliary, probe, metric)
        self.assertLess(result["off_target_overlap_residual"], 1.0e-14)
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)
        self.assertLess(result["transform_orthogonality_residual"], 1.0e-14)

    def test_source_rotation_equations_are_satisfied(self) -> None:
        metric = np.eye(3)
        result = rotate_to_fixed_probe(
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([-0.3, 0.4, 1.0]),
            metric,
        )
        a = result["initial_target_overlap"]
        b = result["initial_auxiliary_overlap"]
        c = result["cosine"]
        s = result["sine"]
        self.assertAlmostEqual(result["achieved_target_overlap"], a * c - b * s)
        self.assertAlmostEqual(result["achieved_auxiliary_overlap"], a * s + b * c)
        self.assertLess(result["stationary_derivative_residual"], 1.0e-14)

    def test_all_input_phase_signs_preserve_observables(self) -> None:
        metric = np.array([[1.0, 0.1, 0.0], [0.1, 1.0, 0.2], [0.0, 0.2, 1.0]])
        target = np.array([1.0, 0.0, 0.0])
        auxiliary = np.array([0.0, 1.0, 0.0])
        probe = np.array([0.3, -0.4, 1.0])
        reference = rotate_to_fixed_probe(target, auxiliary, probe, metric)
        reference_eigenvalues = np.linalg.eigvalsh(reference["rotated_gram"])
        for target_sign in (-1.0, 1.0):
            for auxiliary_sign in (-1.0, 1.0):
                for probe_sign in (-1.0, 1.0):
                    result = rotate_to_fixed_probe(
                        target_sign * target,
                        auxiliary_sign * auxiliary,
                        probe_sign * probe,
                        metric,
                    )
                    self.assertAlmostEqual(
                        abs(result["achieved_target_overlap"]),
                        abs(reference["achieved_target_overlap"]),
                    )
                    np.testing.assert_allclose(
                        np.linalg.eigvalsh(result["rotated_gram"]),
                        reference_eigenvalues,
                        atol=1.0e-14,
                    )

    def test_zero_overlap_vector_is_quarantined(self) -> None:
        with self.assertRaisesRegex(ValueError, "both probe overlaps are zero"):
            rotate_to_fixed_probe(
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.eye(3),
            )


if __name__ == "__main__":
    unittest.main()
