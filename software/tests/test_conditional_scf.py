import unittest

import numpy as np

from ai4orgchem.lfmo.conditional_scf import (
    fixed_group_occupations,
    grouped_nonorthogonal_closed_shell_density,
    grouped_generalized_eigh,
    nonorthogonal_closed_shell_density,
)


class ConditionalScfKernelTests(unittest.TestCase):

    def test_grouped_density_preserves_zero_cross_group_coefficient_block(self) -> None:
        metric = np.array([[1.0, 0.2], [0.2, 1.0]])
        coefficients = np.eye(2)
        density = grouped_nonorthogonal_closed_shell_density(
            coefficients, metric, [1, 1], [1, 1]
        )
        self.assertAlmostEqual(float(density[0, 1]), 0.0, places=14)
        self.assertAlmostEqual(float(np.einsum("ij,ji->", density, metric)), 4.0)

    def test_nonorthogonal_occupied_projector_density_is_idempotent(self) -> None:
        metric = np.array([[1.0, 0.3, 0.1], [0.3, 1.0, 0.2], [0.1, 0.2, 1.0]])
        density = nonorthogonal_closed_shell_density(
            np.eye(3), metric, np.array([2.0, 2.0, 0.0])
        )
        self.assertAlmostEqual(float(np.einsum("ij,ji->", density, metric)), 4.0)
        np.testing.assert_allclose(
            density @ metric @ density, 2.0 * density, atol=1.0e-14
        )

    def test_grouped_solution_masks_both_matrices(self) -> None:
        metric = np.array([[1.0, 0.2, 0.1], [0.2, 1.0, 0.3], [0.1, 0.3, 1.0]])
        fock = np.array([[-1.0, 0.4, 0.2], [0.4, -0.3, 0.5], [0.2, 0.5, 0.7]])
        result = grouped_generalized_eigh(fock, metric, [2, 1])
        self.assertTrue(np.allclose(result["masked_metric"][:2, 2], 0.0))
        self.assertTrue(np.allclose(result["masked_fock"][:2, 2], 0.0))
        self.assertLess(result["maximum_block_generalized_residual"], 1e-12)
        transform = result["transform"]
        self.assertTrue(
            np.allclose(transform.T @ result["masked_metric"] @ transform, np.eye(3), atol=1e-12)
        )

    def test_fixed_group_occupations(self) -> None:
        self.assertEqual(
            fixed_group_occupations([3, 2, 1], [2, 1, 0]).tolist(),
            [2.0, 2.0, 0.0, 2.0, 0.0, 0.0],
        )
        with self.assertRaises(ValueError):
            fixed_group_occupations([1], [2])


if __name__ == "__main__":
    unittest.main()
