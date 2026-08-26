from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.state_masks import (
    apply_symmetric_mask,
    block_mask,
    is_partition_mask,
    metric_diagnostics,
)


class NonorthogonalStateMaskTests(unittest.TestCase):
    def setUp(self) -> None:
        # A deliberately nonidentity, positive-definite overlap metric.
        factor = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.3, 1.0, 0.0, 0.0],
                [0.2, 0.4, 1.0, 0.0],
                [0.1, 0.2, 0.3, 1.0],
            ]
        )
        self.metric = factor @ factor.T

    def test_mask_zeroes_cross_group_overlap_without_identity_assumption(self) -> None:
        mask = block_mask([1, 2, 1])
        masked = apply_symmetric_mask(self.metric, mask)
        self.assertTrue(np.allclose(masked, masked.T))
        self.assertFalse(np.allclose(self.metric, np.eye(4)))
        self.assertEqual(masked[0, 1], 0.0)
        self.assertNotEqual(masked[1, 2], 0.0)

    def test_principal_block_mask_preserves_positive_definiteness(self) -> None:
        masked = apply_symmetric_mask(self.metric, block_mask([1, 2, 1]))
        diagnostics = metric_diagnostics(masked)
        self.assertTrue(diagnostics["symmetric"])
        self.assertTrue(diagnostics["positive_definite"])
        self.assertGreater(diagnostics["minimum_eigenvalue"], 0.0)

    def test_metric_diagnostics_rejects_indefinite_metric(self) -> None:
        diagnostics = metric_diagnostics(np.array([[1.0, 2.0], [2.0, 1.0]]))
        self.assertFalse(diagnostics["positive_definite"])
        self.assertEqual(diagnostics["rank"], 2)
        self.assertEqual(diagnostics["condition_number"], float("inf"))

    def test_metric_diagnostics_reports_exact_rank_deficiency(self) -> None:
        diagnostics = metric_diagnostics(np.array([[1.0, 1.0], [1.0, 1.0]]))
        self.assertEqual(diagnostics["rank"], 1)
        self.assertFalse(diagnostics["full_rank"])
        self.assertFalse(diagnostics["positive_definite"])

    def test_partition_mask_is_an_equivalence_relation(self) -> None:
        self.assertTrue(is_partition_mask(block_mask([1, 2, 1])))
        self.assertFalse(is_partition_mask(np.empty((0, 0))))
        nontransitive = np.array(
            [
                [1.0, 1.0, 0.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0],
            ]
        )
        self.assertFalse(is_partition_mask(nontransitive))

    def test_arbitrary_symmetric_deletion_is_rejected(self) -> None:
        # This binary symmetric mask has a retained diagonal, but it is not a
        # partition. Applied to an SPD correlation matrix, it would produce an
        # indefinite matrix, so it must never enter the protocol path.
        metric = np.full((3, 3), 0.9)
        np.fill_diagonal(metric, 1.0)
        nonpartition = np.array(
            [
                [1.0, 1.0, 0.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0],
            ]
        )
        self.assertTrue(metric_diagnostics(metric)["positive_definite"])
        self.assertLess(np.linalg.eigvalsh(metric * nonpartition)[0], 0.0)
        with self.assertRaises(ValueError):
            apply_symmetric_mask(metric, nonpartition)

    def test_invalid_mask_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            apply_symmetric_mask(self.metric, np.ones((3, 3)))


if __name__ == "__main__":
    unittest.main()
