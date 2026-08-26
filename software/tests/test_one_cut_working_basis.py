from __future__ import annotations

import unittest

import numpy as np

from ai4orgchem.lfmo.working_basis import (
    audit_one_cut_working_basis,
    classify_reflection_weight,
    one_cut_column_metadata,
)


class OneCutWorkingBasisTests(unittest.TestCase):
    def test_reflection_classifier_preserves_mixed_state(self) -> None:
        self.assertEqual(classify_reflection_weight(0.0), "sigma")
        self.assertEqual(classify_reflection_weight(1.0), "pi")
        self.assertEqual(classify_reflection_weight(0.25), "mixed")

    def test_metadata_order_and_roles_are_deterministic(self) -> None:
        records = one_cut_column_metadata(
            np.array([2.0, 1.0, 0.0]),
            target_index=1,
            occupied_indices=[0],
            vacant_indices=[2],
            ch3_pi_weights_before=np.array([0.0, 1.0, 0.0]),
            ch3_pi_weights_after=np.array([0.2, 0.8, 0.0]),
            reference_occupations=np.array([1.0, 0.0]),
            reference_somo_index=0,
        )
        self.assertEqual([item["column"] for item in records], list(range(5)))
        self.assertEqual(
            [item["orbital_role"] for item in records],
            ["cut_single", "fragment_occupied", "fragment_vacant", "reference_single", "reference_vacant"],
        )
        self.assertEqual(records[0]["symmetry_type_after_kost"], "mixed")
        self.assertEqual(records[-1]["symmetry_type_after_kost"], "reference_s")

    def test_metadata_rejects_incomplete_partition(self) -> None:
        with self.assertRaisesRegex(ValueError, "partition"):
            one_cut_column_metadata(
                np.array([2.0, 1.0, 0.0]),
                target_index=1,
                occupied_indices=[0],
                vacant_indices=[],
                ch3_pi_weights_before=np.array([0.0, 1.0, 0.0]),
                ch3_pi_weights_after=np.array([0.0, 1.0, 0.0]),
                reference_occupations=np.array([1.0]),
                reference_somo_index=0,
            )

    def test_full_basis_audit_reconstructs_nonorthogonal_square_basis(self) -> None:
        angle = 0.3
        transform = np.eye(3)
        transform[:2, :2] = np.array(
            [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
        )
        initial_ch3 = np.eye(5)[:, :3]
        transformed_ch3 = initial_ch3 @ transform
        reference = np.eye(5)[:, 3:]
        metric = np.eye(5)
        metric[0, 3] = metric[3, 0] = 0.2
        result = audit_one_cut_working_basis(
            initial_ch3,
            transformed_ch3,
            transform,
            reference,
            metric,
            ch3_ao_indices=[0, 1, 2],
            reference_ao_indices=[3, 4],
        )
        self.assertTrue(result["square_basis"])
        self.assertEqual(result["coefficient_rank"], 5)
        self.assertTrue(result["metric_diagnostics"]["positive_definite"])
        self.assertLess(result["reconstruction_residual"], 1.0e-14)
        self.assertLess(result["metric_covariance_residual"], 1.0e-14)
        self.assertEqual(result["ch3_outside_support_max"], 0.0)
        self.assertEqual(result["reference_outside_support_max"], 0.0)

    def test_phase_and_column_permutations_preserve_metric_spectrum(self) -> None:
        initial_ch3 = np.eye(5)[:, :3]
        reference = np.eye(5)[:, 3:]
        metric = np.eye(5)
        baseline = audit_one_cut_working_basis(
            initial_ch3, initial_ch3, np.eye(3), reference, metric,
            ch3_ao_indices=[0, 1, 2], reference_ao_indices=[3, 4],
        )
        changed = audit_one_cut_working_basis(
            initial_ch3[:, [2, 0, 1]] * np.array([-1.0, 1.0, -1.0]),
            initial_ch3[:, [2, 0, 1]] * np.array([-1.0, 1.0, -1.0]),
            np.eye(3),
            reference[:, [1, 0]] * np.array([-1.0, 1.0]),
            metric,
            ch3_ao_indices=[0, 1, 2], reference_ao_indices=[3, 4],
        )
        np.testing.assert_allclose(
            np.linalg.eigvalsh(baseline["current_metric"]),
            np.linalg.eigvalsh(changed["current_metric"]),
            atol=1.0e-14,
        )


if __name__ == "__main__":
    unittest.main()
