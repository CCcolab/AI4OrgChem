from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.qm.p09_conditional_scf import (
    closed_shell_idempotency_residual,
    generalized_commutator,
)


class P09ConditionalSCFTests(unittest.TestCase):
    def test_generalized_commutator_vanishes_for_diagonal_solution(self) -> None:
        overlap = np.eye(3)
        fock = np.diag([-1.0, -0.2, 0.5])
        density = np.diag([2.0, 2.0, 0.0])
        np.testing.assert_allclose(generalized_commutator(fock, density, overlap), 0.0)

    def test_closed_shell_density_is_idempotent_in_its_metric(self) -> None:
        overlap = np.diag([1.0, 2.0])
        occupied = np.asarray([[1.0], [0.0]])
        density = 2.0 * occupied @ occupied.T
        self.assertLess(closed_shell_idempotency_residual(density, overlap), 1.0e-14)


if __name__ == "__main__":
    unittest.main()
