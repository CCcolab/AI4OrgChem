from __future__ import annotations

import itertools
import unittest
from pathlib import Path

import numpy as np
import yaml

from ai4orgchem.qm.p09_energy_assembly import (
    apply_eri_tensor_mask,
    assemble_restricted_hybrid_energy,
    build_eri_delete_mask,
)
from ai4orgchem.qm.p09_eri_mask import AODescriptor, should_delete_eri


ROOT = Path(__file__).resolve().parents[2]


class P09IndependentEnergyAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mapping = yaml.safe_load(
            (ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.entries = mapping["exchange_integral_classes"]
        cls.descriptors = (
            AODescriptor("sigma"),
            AODescriptor("pi", "A"),
            AODescriptor("pi", "B"),
            AODescriptor("sigma"),
        )

    def test_vectorized_eri_mask_equals_scalar_source_predicate(self) -> None:
        mask = build_eri_delete_mask(self.descriptors, self.entries)
        self.assertEqual(mask.shape, (4, 4, 4, 4))
        for indices in itertools.product(range(4), repeat=4):
            quartet = tuple(self.descriptors[index] for index in indices)
            with self.subTest(indices=indices):
                self.assertEqual(mask[indices], should_delete_eri(quartet, self.entries))

    def test_masked_eri_retains_allowed_and_zeros_forbidden_values(self) -> None:
        eri = np.arange(4**4, dtype=float).reshape((4,) * 4) + 1.0
        masked, delete_mask = apply_eri_tensor_mask(eri, self.descriptors, self.entries)
        self.assertTrue(np.all(masked[delete_mask] == 0.0))
        self.assertTrue(np.array_equal(masked[~delete_mask], eri[~delete_mask]))

    def test_energy_components_match_independent_manual_loops(self) -> None:
        rng = np.random.default_rng(20260821)
        size = 4
        density = rng.normal(size=(size, size))
        density = density + density.T
        hcore = rng.normal(size=(size, size))
        hcore = hcore + hcore.T
        overlap = np.eye(size) + 0.02 * np.ones((size, size))
        xc_potential = rng.normal(size=(size, size))
        xc_potential = 0.5 * (xc_potential + xc_potential.T)
        eri = rng.normal(size=(size,) * 4)
        eri = sum(eri.transpose(axes) for axes in ((0, 1, 2, 3), (1, 0, 2, 3), (0, 1, 3, 2), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 0, 1), (2, 3, 1, 0), (3, 2, 1, 0))) / 8.0
        exact_exchange_fraction = 0.20
        semilocal_xc_energy = -0.37
        nuclear_repulsion = 1.25

        result = assemble_restricted_hybrid_energy(
            density=density,
            hcore=hcore,
            overlap=overlap,
            eri=eri,
            xc_potential=xc_potential,
            semilocal_xc_energy=semilocal_xc_energy,
            exact_exchange_fraction=exact_exchange_fraction,
            nuclear_repulsion=nuclear_repulsion,
            descriptors=self.descriptors,
            source_entries=self.entries,
        )

        manual_j = np.zeros((size, size))
        manual_k = np.zeros((size, size))
        for p, q, r, s in itertools.product(range(size), repeat=4):
            manual_j[p, q] += result["masked_eri"][p, q, r, s] * density[r, s]
            manual_k[p, q] += result["masked_eri"][p, r, q, s] * density[r, s]
        manual_one = sum(
            result["masked_hcore"][p, q] * density[q, p]
            for p, q in itertools.product(range(size), repeat=2)
        )
        manual_coulomb = 0.5 * sum(
            manual_j[p, q] * density[q, p]
            for p, q in itertools.product(range(size), repeat=2)
        )
        manual_exchange = -0.25 * exact_exchange_fraction * sum(
            manual_k[p, q] * density[q, p]
            for p, q in itertools.product(range(size), repeat=2)
        )
        manual_electronic = manual_one + manual_coulomb + manual_exchange + semilocal_xc_energy

        self.assertTrue(np.allclose(result["coulomb_matrix"], manual_j, atol=1.0e-12))
        self.assertTrue(np.allclose(result["exchange_matrix"], manual_k, atol=1.0e-12))
        self.assertAlmostEqual(result["one_electron_energy"], manual_one, places=12)
        self.assertAlmostEqual(result["coulomb_energy"], manual_coulomb, places=12)
        self.assertAlmostEqual(result["exact_exchange_energy"], manual_exchange, places=12)
        self.assertAlmostEqual(result["electronic_energy"], manual_electronic, places=12)
        self.assertAlmostEqual(result["total_energy"], manual_electronic + nuclear_repulsion, places=12)

    def test_conditional_fock_and_metric_cross_pi_blocks_are_zero(self) -> None:
        size = 4
        result = assemble_restricted_hybrid_energy(
            density=np.eye(size),
            hcore=np.ones((size, size)),
            overlap=np.eye(size) + 0.1 * np.ones((size, size)),
            eri=np.ones((size,) * 4),
            xc_potential=np.ones((size, size)),
            semilocal_xc_energy=0.0,
            exact_exchange_fraction=0.2,
            nuclear_repulsion=0.0,
            descriptors=self.descriptors,
            source_entries=self.entries,
        )
        self.assertEqual(result["masked_hcore"][1, 2], 0.0)
        self.assertEqual(result["masked_overlap"][1, 2], 0.0)
        self.assertEqual(result["conditional_fock"][1, 2], 0.0)
        self.assertEqual(result["conditional_fock"][2, 1], 0.0)


if __name__ == "__main__":
    unittest.main()
