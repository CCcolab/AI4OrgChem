import unittest

import numpy as np

from ai4orgchem.lfmo.reflection import adapt_reflection_blocks, occupation_blocks


class ReflectionAdaptationTests(unittest.TestCase):
    def test_blocks_do_not_bridge_or_cross_classes(self) -> None:
        blocks = occupation_blocks(
            [2.0, 2.0 - 0.6e-8, 2.0 - 1.2e-8, 0.0],
            ["occupied", "occupied", "occupied", "vacant"],
            tolerance=1.0e-8,
        )
        self.assertEqual(blocks, [[0, 1], [2], [3]])

    def test_adaptation_is_gauge_invariant_in_physical_space(self) -> None:
        angle = 0.37
        gauge = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        metric = np.eye(4)
        base = np.eye(4)[:, [0, 2]]
        first = adapt_reflection_blocks(
            base, metric, [1, 1, -1, -1], [0.0, 0.0], ["vacant", "vacant"]
        )
        second = adapt_reflection_blocks(
            base @ gauge, metric, [1, 1, -1, -1], [0.0, 0.0], ["vacant", "vacant"]
        )
        self.assertTrue(np.allclose(first["coefficients"], second["coefficients"], atol=1e-12))
        self.assertLess(first["maximum_parity_residual"], 1e-12)
        self.assertLess(first["full_subspace_projector_residual"], 1e-12)

    def test_non_closed_block_is_rejected(self) -> None:
        coefficient = np.array([[1.0], [1.0]]) / np.sqrt(2.0)
        with self.assertRaisesRegex(RuntimeError, "not closed"):
            adapt_reflection_blocks(
                coefficient, np.eye(2), [1, -1], [0.0], ["vacant"]
            )

    def test_accepts_nondiagonal_reflection_operator(self) -> None:
        reflection = np.array([[0.0, 1.0], [1.0, 0.0]])
        coefficients = np.array([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2.0)
        result = adapt_reflection_blocks(
            coefficients,
            np.eye(2),
            reflection,
            [0.0, 0.0],
            ["vacant", "vacant"],
        )
        self.assertLess(result["maximum_parity_residual"], 1.0e-12)
        self.assertLess(result["orthonormality_after_residual"], 1.0e-12)

    def test_spectral_sign_policy_types_a_nearly_closed_block(self) -> None:
        angle = 0.05
        coefficient = np.array([[np.cos(angle)], [np.sin(angle)]])
        result = adapt_reflection_blocks(
            coefficient,
            np.eye(2),
            [1, -1],
            [0.0],
            ["vacant"],
            classification_policy="spectral_sign",
            minimum_absolute_eigenvalue=0.99,
        )
        self.assertEqual(result["blocks"][0]["adapted_parities"], ["sigma"])
        self.assertGreater(
            abs(result["blocks"][0]["input_reflection_eigenvalues"][0]), 0.99
        )

    def test_spectral_sign_policy_rejects_a_closed_gap(self) -> None:
        coefficient = np.array([[1.0], [1.0]]) / np.sqrt(2.0)
        with self.assertRaisesRegex(RuntimeError, "spectral gap"):
            adapt_reflection_blocks(
                coefficient,
                np.eye(2),
                [1, -1],
                [0.0],
                ["vacant"],
                classification_policy="spectral_sign",
                minimum_absolute_eigenvalue=0.99,
            )


if __name__ == "__main__":
    unittest.main()
