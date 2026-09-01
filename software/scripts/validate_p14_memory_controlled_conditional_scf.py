"""Compare reference and memory-controlled P14 conditional SCF at STO-3G."""

from __future__ import annotations

import argparse
import json
import resource
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ai4orgchem.qm.p09_ao_classification import classify_planar_pyscf_aos
from ai4orgchem.qm.p09_conditional_scf import run_p09_conditional_rks
from run_p14_benzotricyclobutadiene_smoke import (
    build_mean_field,
    build_molecule,
    d3h_atoms,
    ordinary_state,
    write_json,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
DEFAULT_CLASSES = ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_memory_controlled_eri_equivalence_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_memory_controlled_eri_equivalence.md"


def compact(result: dict[str, Any]) -> dict[str, Any]:
    excluded = {"density", "mo_coefficients", "mo_energies_hartree", "mo_occupations", "history"}
    return {key: value for key, value in result.items() if key not in excluded}


def run_conditional(
    atoms: list[list[Any]],
    protocol: dict[str, Any],
    classes: dict[str, Any],
    initial_density: np.ndarray,
    *,
    memory_controlled_eri: bool,
) -> dict[str, Any]:
    molecule = build_molecule(atoms, protocol)
    mean_field = build_mean_field(molecule, protocol)
    descriptors = classify_planar_pyscf_aos(
        molecule, {index: "A" if index < 6 else "B" for index in range(12)}
    )
    options = protocol["smoke_gate"]["conditional_scf"]
    return run_p09_conditional_rks(
        mean_field,
        descriptors,
        classes["exchange_integral_classes"],
        initial_density=initial_density,
        maximum_cycles=int(options["maximum_cycles"]),
        density_tolerance=float(options["density_tolerance"]),
        energy_tolerance=float(options["energy_tolerance_hartree"]),
        diis_start_cycle=int(options["diis_start_cycle"]),
        diis_space=int(options["diis_space"]),
        damping_cycles=int(options["damping_cycles"]),
        damping=float(options["damping"]),
        memory_controlled_eri=memory_controlled_eri,
    )


def render_report(record: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# P14内存收缩条件SCF等价性验证",
            "",
            "- 体系：10-12号C12H6，source-PLG描述符几何。",
            "- 层级：B3LYPG/STO-3G。",
            "- 比较：旧复制+四维布尔掩码与新单ERI张量原位类别块掩码。",
            f"- 总能差：`{record['differences']['total_energy_hartree']:.3e} Eh`。",
            f"- 删除元素计数差：`{record['differences']['deleted_eri_count']}`。",
            f"- 密度Frobenius差：`{record['differences']['density_frobenius_norm']:.3e}`。",
            f"- 结论：`{record['verdict']}`。",
            "",
        ]
    )


def run(protocol_path: Path, classes_path: Path) -> dict[str, Any]:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    source = protocol["source_anchors_B3LYP_6_31G_star"]["PLG"]
    atoms = d3h_atoms(source, float(protocol["smoke_gate"]["fixed_CH_angstrom"]))
    ordinary = ordinary_state(atoms, protocol)
    initial_density = np.asarray(ordinary["density"], dtype=float)
    reference = run_conditional(
        atoms, protocol, classes, initial_density, memory_controlled_eri=False
    )
    candidate = run_conditional(
        atoms, protocol, classes, initial_density, memory_controlled_eri=True
    )
    differences = {
        "total_energy_hartree": abs(float(candidate["total_energy_hartree"]) - float(reference["total_energy_hartree"])),
        "density_frobenius_norm": float(np.linalg.norm(np.asarray(candidate["density"]) - np.asarray(reference["density"]), ord="fro")),
        "deleted_eri_count": int(candidate["deleted_eri_count"]) - int(reference["deleted_eri_count"]),
        "deleted_eri_fraction": abs(float(candidate["deleted_eri_fraction"]) - float(reference["deleted_eri_fraction"])),
        "one_electron_energy_hartree": abs(float(candidate["one_electron_energy_hartree"]) - float(reference["one_electron_energy_hartree"])),
        "coulomb_energy_hartree": abs(float(candidate["coulomb_energy_hartree"]) - float(reference["coulomb_energy_hartree"])),
        "exact_exchange_energy_hartree": abs(float(candidate["exact_exchange_energy_hartree"]) - float(reference["exact_exchange_energy_hartree"])),
    }
    checks = {
        "reference_converged": bool(reference["converged"]),
        "memory_controlled_converged": bool(candidate["converged"]),
        "total_energy_equal": differences["total_energy_hartree"] <= 1.0e-10,
        "density_equal": differences["density_frobenius_norm"] <= 1.0e-9,
        "deleted_count_equal": differences["deleted_eri_count"] == 0,
        "deleted_fraction_equal": differences["deleted_eri_fraction"] <= 1.0e-15,
        "one_electron_equal": differences["one_electron_energy_hartree"] <= 1.0e-10,
        "coulomb_equal": differences["coulomb_energy_hartree"] <= 1.0e-10,
        "exact_exchange_equal": differences["exact_exchange_energy_hartree"] <= 1.0e-10,
        "single_tensor_mode_reported": candidate["eri_storage_mode"] == "single_tensor_inplace_category_mask",
    }
    return {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "stage": "memory_controlled_eri_equivalence",
        "reference": compact(reference),
        "memory_controlled": compact(candidate),
        "differences": differences,
        "acceptance_checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "peak_rss_mib": float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0,
        "scientific_classification_allowed": False,
        "production_label": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    record = run(arguments.protocol, arguments.classes)
    write_json(arguments.output, record)
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(render_report(record), encoding="utf-8")
    print(json.dumps({
        "verdict": record["verdict"],
        "total_energy_difference_hartree": record["differences"]["total_energy_hartree"],
        "density_difference_frobenius": record["differences"]["density_frobenius_norm"],
        "deleted_eri_count_difference": record["differences"]["deleted_eri_count"],
        "peak_rss_mib": record["peak_rss_mib"],
        "output": str(arguments.output),
    }, ensure_ascii=False), flush=True)
    return 0 if record["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
