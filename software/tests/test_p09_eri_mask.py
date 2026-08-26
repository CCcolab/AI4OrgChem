from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from ai4orgchem.qm.p09_eri_mask import (
    AODescriptor,
    chemist_eightfold_permutations,
    matches_index_predicate,
    should_delete_eri,
)


ROOT = Path(__file__).resolve().parents[2]


def sigma() -> AODescriptor:
    return AODescriptor("sigma")


def pi(fragment: str) -> AODescriptor:
    return AODescriptor("pi", fragment)


class P09Figure84ERIMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mapping = yaml.safe_load(
            (ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.entries = mapping["exchange_integral_classes"]
        cls.by_id = {entry["id"]: entry for entry in cls.entries}

    def test_all_fifteen_source_classes_have_an_ordered_forbidden_witness(self) -> None:
        s = sigma()
        a, b = pi("A"), pi("B")
        witnesses = {
            "X01": (s, s, a, b),
            "X02": (s, s, a, b),
            "X03": (a, a, a, b),
            "X04": (a, a, a, b),
            "X05": (a, a, a, b),
            "X06": (b, b, a, b),
            "X07": (b, b, a, b),
            "X08": (b, a, b, b),
            "X09": (s, a, s, b),
            "X10": (s, b, s, a),
            "X11": (a, b, s, s),
            "X12": (a, b, a, a),
            "X13": (a, b, b, b),
            "X14": (a, b, a, b),
            "X15": (a, b, a, b),
        }
        self.assertEqual(set(witnesses), set(self.by_id))
        for class_id, quartet in witnesses.items():
            with self.subTest(class_id=class_id):
                self.assertTrue(
                    matches_index_predicate(quartet, self.by_id[class_id]["index_predicate"])
                )

    def test_every_forbidden_witness_is_closed_under_eightfold_eri_symmetry(self) -> None:
        s = sigma()
        forbidden = (
            (s, s, pi("A"), pi("B")),
            (pi("A"), pi("A"), pi("A"), pi("B")),
            (pi("B"), pi("B"), pi("A"), pi("B")),
            (s, pi("A"), s, pi("B")),
            (pi("A"), pi("B"), pi("A"), pi("B")),
        )
        for quartet in forbidden:
            for permutation in chemist_eightfold_permutations(quartet):
                with self.subTest(quartet=quartet, permutation=permutation):
                    self.assertTrue(should_delete_eri(permutation, self.entries))

    def test_explicit_allowed_integrals_survive_all_permutations(self) -> None:
        s = sigma()
        allowed = (
            (s, s, s, s),
            (s, s, pi("A"), pi("A")),
            (s, pi("A"), s, pi("A")),
            (pi("A"), pi("A"), pi("B"), pi("B")),
        )
        for quartet in allowed:
            for permutation in chemist_eightfold_permutations(quartet):
                with self.subTest(quartet=quartet, permutation=permutation):
                    self.assertFalse(should_delete_eri(permutation, self.entries))

    def test_same_fragment_substitution_does_not_satisfy_cross_fragment_classes(self) -> None:
        same_fragment = (pi("A"), pi("A"), pi("A"), pi("A"))
        self.assertFalse(should_delete_eri(same_fragment, self.entries))

    def test_invalid_ao_descriptors_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AODescriptor("pi")
        with self.assertRaises(ValueError):
            AODescriptor("delta", "A")


if __name__ == "__main__":
    unittest.main()
