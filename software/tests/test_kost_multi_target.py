from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.kost import bounded_multi_target_kost


class KostMultiTargetTests(unittest.TestCase):
    def test_two_targets_localize_against_shared_auxiliaries(self) -> None:
        basis = np.eye(8)
        targets = basis[:, :2]
        occupied = basis[:, 2:4]
        vacant = basis[:, 4:7]
        probes = np.column_stack(
            (
                np.array([1.0, 0.10, 0.30, -0.20, 0.40, 0.15, -0.10, 0.0]),
                np.array([0.05, 1.0, -0.25, 0.35, 0.10, -0.30, 0.20, 0.0]),
            )
        )
        result = bounded_multi_target_kost(
            targets,
            occupied,
            vacant,
            probes,
            np.eye(8),
            maximum_macro_cycles=20,
        )
        self.assertTrue(result["scheduler_quiescent"])
        self.assertLess(result["maximum_auxiliary_probe_overlap"], 1.0e-10)
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)
        np.testing.assert_allclose(
            result["current_block"],
            np.column_stack((targets, occupied, vacant))
            @ result["cumulative_transform"],
            atol=1.0e-14,
        )


if __name__ == "__main__":
    unittest.main()
