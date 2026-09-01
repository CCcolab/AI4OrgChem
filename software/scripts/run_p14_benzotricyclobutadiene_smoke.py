"""Run the frozen P14 C12H6 fixed-geometry technical smoke calculation."""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ai4orgchem.qm.p09_ao_classification import classify_planar_pyscf_aos
from ai4orgchem.qm.p09_conditional_scf import run_p09_conditional_rks


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml"
DEFAULT_CLASSES = ROOT / "configs/qm/p09_exchange_integral_classes_v0.1.yaml"
DEFAULT_OUTPUT = ROOT / "runs/reproduction/p14/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json"
DEFAULT_REPORT = ROOT / "runs/reproduction/p14/p14_benzotricyclobutadiene_fixed_geometry_smoke.md"
HARTREE_TO_KCAL_PER_MOL = 627.5094740631


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def d3h_atoms(parameters: dict[str, float], ch_length: float) -> list[list[Any]]:
    """Construct planar D3h C12H6 from the five source geometry parameters."""

    rendo = float(parameters["rendo_angstrom"])
    rexo = float(parameters["rexo_angstrom"])
    rside = float(parameters["rside_angstrom"])
    router = float(parameters["router_angstrom"])
    edge_lengths = [rendo, rexo] * 3
    edge_angles = np.deg2rad([120.0, 180.0, 240.0, 300.0, 0.0, 60.0])
    central = np.zeros((6, 2), dtype=float)
    for index in range(5):
        central[index + 1] = central[index] + edge_lengths[index] * np.asarray(
            [np.cos(edge_angles[index]), np.sin(edge_angles[index])]
        )
    closure = central[5] + edge_lengths[5] * np.asarray(
        [np.cos(edge_angles[5]), np.sin(edge_angles[5])]
    )
    if float(np.linalg.norm(closure - central[0])) > 1.0e-10:
        raise ValueError("alternating D3h central ring did not close")
    central -= np.mean(central, axis=0)

    outer: list[np.ndarray] = []
    fused_pairs = ((0, 1), (2, 3), (4, 5))
    height_squared = rside**2 - (0.5 * (rendo - router)) ** 2
    if height_squared <= 0.0:
        raise ValueError("source parameters cannot form the annulated four-membered rings")
    height = float(np.sqrt(height_squared))
    for first, second in fused_pairs:
        tangent = central[second] - central[first]
        tangent /= np.linalg.norm(tangent)
        midpoint = 0.5 * (central[first] + central[second])
        outward = midpoint / np.linalg.norm(midpoint)
        outer_midpoint = midpoint + height * outward
        outer.extend(
            [
                outer_midpoint - 0.5 * router * tangent,
                outer_midpoint + 0.5 * router * tangent,
            ]
        )
    outer_array = np.asarray(outer, dtype=float)

    hydrogens: list[np.ndarray] = []
    for pair_index, (first, second) in enumerate(fused_pairs):
        left = outer_array[2 * pair_index]
        right = outer_array[2 * pair_index + 1]
        for atom, central_neighbor, outer_neighbor in (
            (left, central[first], right),
            (right, central[second], left),
        ):
            direction = -(
                (central_neighbor - atom) / np.linalg.norm(central_neighbor - atom)
                + (outer_neighbor - atom) / np.linalg.norm(outer_neighbor - atom)
            )
            direction /= np.linalg.norm(direction)
            hydrogens.append(atom + float(ch_length) * direction)

    carbons = np.vstack((central, outer_array))
    return [
        *[["C", float(x), float(y), 0.0] for x, y in carbons],
        *[["H", float(x), float(y), 0.0] for x, y in hydrogens],
    ]


def geometry_metrics(atoms: list[list[Any]]) -> dict[str, float]:
    xyz = np.asarray([row[1:4] for row in atoms], dtype=float)
    fused = ((0, 1), (2, 3), (4, 5))
    nonfused = ((1, 2), (3, 4), (5, 0))
    sides = ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11))
    outer = ((6, 7), (8, 9), (10, 11))

    def mean_distance(pairs: tuple[tuple[int, int], ...]) -> float:
        return float(np.mean([np.linalg.norm(xyz[i] - xyz[j]) for i, j in pairs]))

    rendo = mean_distance(fused)
    rexo = mean_distance(nonfused)
    return {
        "rendo_angstrom": rendo,
        "rexo_angstrom": rexo,
        "delta_r_angstrom": rendo - rexo,
        "rside_angstrom": mean_distance(sides),
        "router_angstrom": mean_distance(outer),
        "maximum_out_of_plane_angstrom": float(np.max(np.abs(xyz[:, 2]))),
    }


def build_molecule(atoms: list[list[Any]], protocol: dict[str, Any]) -> Any:
    from pyscf import gto

    smoke = protocol["smoke_gate"]
    system = protocol["system"]
    return gto.M(
        atom=atoms,
        basis=str(smoke["basis"]),
        charge=int(system["charge"]),
        spin=int(system["multiplicity"]) - 1,
        unit="Angstrom",
        symmetry=False,
        verbose=0,
    )


def build_mean_field(molecule: Any, protocol: dict[str, Any]) -> Any:
    from pyscf import dft

    smoke = protocol["smoke_gate"]
    mean_field = dft.RKS(molecule)
    mean_field.verbose = 0
    mean_field.xc = str(smoke["pyscf_xc"])
    mean_field.grids.level = int(smoke["grid_level"])
    mean_field.conv_tol = float(smoke["scf_tolerance_hartree"])
    mean_field.max_cycle = int(smoke["maximum_scf_cycles"])
    mean_field.max_memory = int(smoke["maximum_memory_mb"])
    return mean_field


def ordinary_state(atoms: list[list[Any]], protocol: dict[str, Any]) -> dict[str, Any]:
    molecule = build_molecule(atoms, protocol)
    mean_field = build_mean_field(molecule, protocol)
    energy = float(mean_field.kernel())
    density = np.asarray(mean_field.make_rdm1(), dtype=float)
    overlap = np.asarray(mean_field.get_ovlp(), dtype=float)
    return {
        "converged": bool(mean_field.converged),
        "total_energy_hartree": energy,
        "electronic_energy_hartree": energy - float(molecule.energy_nuc()),
        "nuclear_repulsion_hartree": float(molecule.energy_nuc()),
        "physical_metric_electron_count": float(np.einsum("pq,qp->", overlap, density)),
        "density": density,
    }


def compact_state(state: dict[str, Any]) -> dict[str, Any]:
    excluded = {"density", "mo_coefficients", "mo_energies_hartree", "mo_occupations"}
    return {key: value for key, value in state.items() if key not in excluded}


def render_report(record: dict[str, Any]) -> str:
    checks = record["acceptance_checks"]
    return "\n".join(
        [
            "# P14 C12H6固定几何技术烟测",
            "",
            f"- 协议：`{record['protocol_id']}`",
            "- 体系：原著10-12号benzotricyclobutadiene，C12H6。",
            "- 层级：B3LYPG/STO-3G，仅验证实现，不参与科学分类。",
            f"- 门禁：`{record['smoke_gate_verdict']}`（{sum(checks.values())}/{len(checks)}项通过）。",
            "",
            "| 状态 | 能量 (Eh) | 电子数 |",
            "|---|---:|---:|",
            f"| ordinary@source-G | {record['ordinary_G']['total_energy_hartree']:+.10f} | {record['ordinary_G']['physical_metric_electron_count']:.8f} |",
            f"| ordinary@source-PLG | {record['ordinary_at_PLG']['total_energy_hartree']:+.10f} | {record['ordinary_at_PLG']['physical_metric_electron_count']:.8f} |",
            f"| conditional-PLG@source-PLG | {record['conditional_PLG']['total_energy_hartree']:+.10f} | {record['conditional_PLG']['masked_metric_electron_count']:.8f} |",
            "",
            f"固定描述符端点`E(ordinary@G)-E(conditional-PLG@PLG)={record['technical_endpoint_kcal_mol']:+.6f} kcal/mol`。该值使用STO-3G，不解释为原著B3LYP/6-31G*的π-distortivity能量。",
            "",
        ]
    )


def run(protocol_path: Path, classes_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    smoke = protocol["smoke_gate"]
    source = protocol["source_anchors_B3LYP_6_31G_star"]
    ch_length = float(smoke["fixed_CH_angstrom"])
    g_atoms = d3h_atoms(source["G"], ch_length)
    plg_atoms = d3h_atoms(source["PLG"], ch_length)
    g_metrics = geometry_metrics(g_atoms)
    plg_metrics = geometry_metrics(plg_atoms)

    ordinary_g_raw = ordinary_state(g_atoms, protocol)
    if not ordinary_g_raw["converged"]:
        raise RuntimeError("ordinary source-G smoke state did not converge")
    ordinary_plg_raw = ordinary_state(plg_atoms, protocol)
    if not ordinary_plg_raw["converged"]:
        raise RuntimeError("ordinary source-PLG smoke state did not converge")

    molecule = build_molecule(plg_atoms, protocol)
    mean_field = build_mean_field(molecule, protocol)
    fragment_map = {index: "A" if index < 6 else "B" for index in range(12)}
    descriptors = classify_planar_pyscf_aos(molecule, fragment_map)
    options = smoke["conditional_scf"]
    conditional_raw = run_p09_conditional_rks(
        mean_field,
        descriptors,
        classes["exchange_integral_classes"],
        initial_density=np.asarray(ordinary_plg_raw["density"], dtype=float),
        maximum_cycles=int(options["maximum_cycles"]),
        density_tolerance=float(options["density_tolerance"]),
        energy_tolerance=float(options["energy_tolerance_hartree"]),
        diis_start_cycle=int(options["diis_start_cycle"]),
        diis_space=int(options["diis_space"]),
        damping_cycles=int(options["damping_cycles"]),
        damping=float(options["damping"]),
    )

    acceptance = smoke["acceptance"]
    expected_electrons = float(acceptance["electron_count"])
    electron_tolerance = float(acceptance["electron_count_tolerance"])
    geometry_tolerance = 1.0e-10
    checks = {
        "ordinary_G_converged": bool(ordinary_g_raw["converged"]),
        "ordinary_at_PLG_converged": bool(ordinary_plg_raw["converged"]),
        "conditional_PLG_converged": bool(conditional_raw["converged"]),
        "ordinary_G_78_electrons": abs(float(ordinary_g_raw["physical_metric_electron_count"]) - expected_electrons) <= electron_tolerance,
        "ordinary_at_PLG_78_electrons": abs(float(ordinary_plg_raw["physical_metric_electron_count"]) - expected_electrons) <= electron_tolerance,
        "conditional_PLG_78_electrons": abs(float(conditional_raw["masked_metric_electron_count"]) - expected_electrons) <= electron_tolerance,
        "G_source_geometry_reconstructed": max(abs(float(g_metrics[key]) - float(source["G"][key])) for key in ("rendo_angstrom", "rexo_angstrom", "rside_angstrom", "router_angstrom")) <= geometry_tolerance,
        "PLG_source_geometry_reconstructed": max(abs(float(plg_metrics[key]) - float(source["PLG"][key])) for key in ("rendo_angstrom", "rexo_angstrom", "rside_angstrom", "router_angstrom")) <= geometry_tolerance,
        "interfragment_pi_overlap_zero": float(conditional_raw["masked_overlap_cross_pi_max_abs"]) <= float(acceptance["matrix_zero_tolerance"]),
        "interfragment_pi_fock_zero": float(conditional_raw["conditional_fock_cross_pi_max_abs"]) <= float(acceptance["matrix_zero_tolerance"]),
        "exchange_integrals_deleted": int(conditional_raw["deleted_eri_count"]) > 0,
        "energy_components_close": float(conditional_raw["energy_component_closure_residual_hartree"]) <= float(acceptance["energy_component_closure_hartree"]),
        "commutator_closed": float(conditional_raw["final_commutator_frobenius_norm"]) <= float(acceptance["commutator_frobenius_tolerance"]),
        "density_idempotent": float(conditional_raw["closed_shell_idempotency_relative_residual"]) <= float(acceptance["idempotency_relative_tolerance"]),
        "scientific_classification_disabled": smoke["scientific_classification_allowed"] is False,
    }
    technical_endpoint = (
        float(ordinary_g_raw["total_energy_hartree"])
        - float(conditional_raw["total_energy_hartree"])
    ) * HARTREE_TO_KCAL_PER_MOL
    peak_rss_mib = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    record = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "proposition_id": "P14",
        "stage": "fixed_source_geometry_STO3G_technical_smoke",
        "scientific_classification_allowed": False,
        "G_geometry": {"atoms_angstrom": g_atoms, "metrics": g_metrics},
        "PLG_geometry": {"atoms_angstrom": plg_atoms, "metrics": plg_metrics},
        "ordinary_G": compact_state(ordinary_g_raw),
        "ordinary_at_PLG": compact_state(ordinary_plg_raw),
        "conditional_PLG": compact_state(conditional_raw),
        "technical_endpoint_kcal_mol": technical_endpoint,
        "acceptance_checks": checks,
        "smoke_gate_verdict": "PASS" if all(checks.values()) else "FAIL",
        "wall_time_seconds": time.perf_counter() - started,
        "peak_rss_mib": peak_rss_mib,
        "thread_count": 8,
        "production_label": False,
        "training_eligible": False,
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    record = run(arguments.protocol.resolve(), arguments.classes.resolve())
    write_json(arguments.output.resolve(), record)
    arguments.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    arguments.report.resolve().write_text(render_report(record), encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": record["smoke_gate_verdict"],
                "technical_endpoint_kcal_mol": record["technical_endpoint_kcal_mol"],
                "wall_time_seconds": record["wall_time_seconds"],
                "peak_rss_mib": record["peak_rss_mib"],
                "output": str(arguments.output.resolve()),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0 if record["smoke_gate_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
