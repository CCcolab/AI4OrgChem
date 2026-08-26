from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.gl2014 import zero_cross_blocks


class P08GL2014HelperTests(unittest.TestCase):
    def test_zero_cross_blocks_preserves_other_elements(self) -> None:
        matrix = np.arange(36, dtype=float).reshape(6, 6)
        matrix = matrix + matrix.T + np.eye(6)
        left = np.asarray([0, 2])
        right = np.asarray([3, 5])
        result = zero_cross_blocks(matrix, left, right)
        self.assertTrue(np.allclose(result[np.ix_(left, right)], 0.0))
        self.assertTrue(np.allclose(result[np.ix_(right, left)], 0.0))
        self.assertEqual(result[1, 4], matrix[1, 4])
        self.assertTrue(np.allclose(result, result.T))


if __name__ == "__main__":
    unittest.main()

