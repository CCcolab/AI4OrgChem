from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.subspaces import (
    metric_projector,
    projector_diagnostics,
    subspace_leakage,
)


class NonorthogonalSubspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        factor = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.3, 1.0, 0.0, 0.0],
                [0.1, 0.2, 1.0, 0.0],
                [0.2, 0.1, 0.3, 1.0],
            ]
        )
        self.metric = factor @ factor.T
        self.basis = np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.2, 0.1],
                [0.0, 0.3],
            ]
        )

    def test_projector_is_idempotent_and_metric_self_adjoint(self) -> None:
        diagnostics = projector_diagnostics(self.metric, self.basis)
        self.assertEqual(diagnostics["rank"], 2)
        self.assertAlmostEqual(diagnostics["trace"], 2.0, places=12)
        self.assertLess(diagnostics["idempotency_residual"], 1.0e-12)
        self.assertLess(diagnostics["metric_self_adjoint_residual"], 1.0e-12)
        # A nonorthogonal-metric projector generally is not Euclidean symmetric.
        self.assertGreater(diagnostics["euclidean_symmetry_residual"], 1.0e-3)

    def test_projector_is_invariant_to_subspace_gauge(self) -> None:
        reference = metric_projector(self.metric, self.basis)
        transformations = (
            np.array([[-1.0, 0.0], [0.0, 1.0]]),
            np.array([[0.0, 1.0], [1.0, 0.0]]),
            np.array([[1.0, 0.4], [-0.2, 1.3]]),
        )
        for transform in transformations:
            transformed = metric_projector(self.metric, self.basis @ transform)
            self.assertTrue(np.allclose(reference, transformed, atol=1.0e-12))

    def test_leakage_is_zero_one_and_controlled_for_orthogonal_spaces(self) -> None:
        metric = np.eye(4)
        sigma = np.eye(4)[:, :2]
        pi = np.eye(4)[:, 2:]
        self.assertEqual(subspace_leakage(metric, sigma, pi), 0.0)
        self.assertAlmostEqual(subspace_leakage(metric, pi, pi), 1.0, places=14)

        theta = 0.2
        mixed = np.cos(theta) * sigma + np.sin(theta) * pi
        self.assertAlmostEqual(
            subspace_leakage(metric, mixed, pi), np.sin(theta) ** 2, places=14
        )

    def test_leakage_is_gauge_invariant(self) -> None:
        metric = np.eye(4)
        sigma = np.eye(4)[:, :2]
        pi = np.eye(4)[:, 2:]
        mixed = 0.8 * sigma + 0.6 * pi
        source_gauge = np.array([[1.0, 0.3], [0.2, 1.2]])
        forbidden_gauge = np.array([[0.0, -2.0], [0.5, 0.0]])
        reference = subspace_leakage(metric, mixed, pi)
        transformed = subspace_leakage(
            metric, mixed @ source_gauge, pi @ forbidden_gauge
        )
        self.assertAlmostEqual(reference, transformed, places=13)

    def test_leakage_limits_hold_in_a_nonorthogonal_metric(self) -> None:
        forbidden = self.basis
        constraint = forbidden.T @ self.metric
        _, _, right_vectors = np.linalg.svd(constraint)
        complement = right_vectors[constraint.shape[0] :].T
        self.assertAlmostEqual(
            subspace_leakage(self.metric, complement, forbidden), 0.0, places=13
        )
        self.assertAlmostEqual(
            subspace_leakage(self.metric, forbidden, forbidden), 1.0, places=13
        )

    def test_rank_deficient_subspace_is_rejected(self) -> None:
        duplicate = np.column_stack((self.basis[:, 0], self.basis[:, 0]))
        with self.assertRaises(ValueError):
            metric_projector(self.metric, duplicate)


if __name__ == "__main__":
    unittest.main()
