from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GEOMETRY = ROOT / "data" / "processed" / "p09_benzene_G_DSI3_smoke_v0.1.json"
DEFAULT_OUTPUT = ROOT / "configs" / "science_v0.2" / "wp3_symmetry_mode_seeds.json"
MASSES = {"C": 12.011, "H": 1.008}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_geometry(path: Path) -> tuple[list[str], np.ndarray, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["optimized_G_geometry"]["atoms_angstrom"]
    symbols = [row[0] for row in rows]
    coordinates = np.array([row[1:] for row in rows], dtype=float)
    if symbols != ["C"] * 6 + ["H"] * 6 or coordinates.shape != (12, 3):
        raise ValueError("WP3 seed generator requires the frozen six-carbon/six-hydrogen benzene ordering")
    return symbols, coordinates, payload["optimized_G_geometry"]["geometry_sha256"].lower()


def bond_sum(coordinates: np.ndarray, weights: np.ndarray) -> float:
    total = 0.0
    for index in range(6):
        neighbor = (index + 1) % 6
        total += float(weights[index]) * np.linalg.norm(coordinates[neighbor] - coordinates[index])
    return total


def angle(a: np.ndarray, center: np.ndarray, b: np.ndarray) -> float:
    left = a - center
    right = b - center
    cosine = float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right)))
    return math.acos(max(-1.0, min(1.0, cosine)))


def angle_sum(coordinates: np.ndarray, weights: np.ndarray) -> float:
    total = 0.0
    for index in range(6):
        total += float(weights[index]) * angle(
            coordinates[(index - 1) % 6], coordinates[index], coordinates[(index + 1) % 6]
        )
    return total


def numerical_gradient(function: Callable[[np.ndarray], float], coordinates: np.ndarray) -> np.ndarray:
    epsilon = 1.0e-6
    gradient = np.zeros_like(coordinates)
    for atom in range(coordinates.shape[0]):
        for axis in range(3):
            plus = coordinates.copy()
            minus = coordinates.copy()
            plus[atom, axis] += epsilon
            minus[atom, axis] -= epsilon
            gradient[atom, axis] = (function(plus) - function(minus)) / (2.0 * epsilon)
    return gradient


def rigid_basis(coordinates: np.ndarray, masses: np.ndarray) -> np.ndarray:
    center_of_mass = np.average(coordinates, axis=0, weights=masses)
    centered = coordinates - center_of_mass
    sqrt_mass = np.sqrt(masses)
    candidates: list[np.ndarray] = []
    for axis in range(3):
        vector = np.zeros_like(coordinates)
        vector[:, axis] = sqrt_mass
        candidates.append(vector.reshape(-1))
    axes = np.eye(3)
    for axis in axes:
        vector = np.cross(np.broadcast_to(axis, centered.shape), centered)
        vector *= sqrt_mass[:, None]
        candidates.append(vector.reshape(-1))
    matrix = np.column_stack(candidates)
    u, singular_values, _ = np.linalg.svd(matrix, full_matrices=False)
    rank = int(np.sum(singular_values > 1.0e-10))
    return u[:, :rank]


def project_and_normalize(vector: np.ndarray, rigid: np.ndarray, previous: list[np.ndarray]) -> np.ndarray:
    candidate = vector.reshape(-1).astype(float)
    candidate -= rigid @ (rigid.T @ candidate)
    for basis in previous:
        candidate -= basis * float(np.dot(basis, candidate))
    norm = float(np.linalg.norm(candidate))
    if norm < 1.0e-12:
        raise ValueError("symmetry coordinate collapsed after projection")
    return candidate / norm


def c6_transform(vector: np.ndarray) -> np.ndarray:
    theta = math.pi / 3.0
    rotation = np.array(
        [[math.cos(theta), -math.sin(theta), 0.0], [math.sin(theta), math.cos(theta), 0.0], [0.0, 0.0, 1.0]]
    )
    source = vector.reshape(12, 3)
    transformed = np.zeros_like(source)
    for index in range(6):
        transformed[(index + 1) % 6] = rotation @ source[index]
        transformed[6 + (index + 1) % 6] = rotation @ source[6 + index]
    return transformed.reshape(-1)


def inversion_transform(vector: np.ndarray) -> np.ndarray:
    source = vector.reshape(12, 3)
    transformed = np.zeros_like(source)
    for index in range(6):
        transformed[(index + 3) % 6] = -source[index]
        transformed[6 + (index + 3) % 6] = -source[6 + index]
    return transformed.reshape(-1)


def rounded_matrix(vector: np.ndarray) -> list[list[float]]:
    return np.round(vector.reshape(12, 3), 14).tolist()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate non-QM symmetry-adapted WP3 benzene mode seeds")
    parser.add_argument("--geometry", type=Path, default=DEFAULT_GEOMETRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    symbols, coordinates, geometry_contract_hash = load_geometry(args.geometry)
    masses = np.array([MASSES[symbol] for symbol in symbols])
    rigid = rigid_basis(coordinates, masses)
    sqrt_mass = np.sqrt(masses)[:, None]

    phases = np.arange(6, dtype=float) * (2.0 * math.pi / 6.0)
    coordinate_functions: list[tuple[str, str, Callable[[np.ndarray], float]]] = [
        ("B2u_BLA", "B2u", lambda xyz: bond_sum(xyz, (-1.0) ** np.arange(6))),
        ("A1g_breathing", "A1g", lambda xyz: bond_sum(xyz, np.ones(6))),
        ("E2g_bend_cos", "E2g", lambda xyz: angle_sum(xyz, np.cos(2.0 * phases))),
        ("E2g_bend_sin", "E2g", lambda xyz: angle_sum(xyz, np.sin(2.0 * phases))),
    ]

    modes: list[np.ndarray] = []
    mode_rows: list[dict[str, object]] = []
    for name, irrep, function in coordinate_functions:
        cartesian_gradient = numerical_gradient(function, coordinates)
        mass_weighted_gradient = cartesian_gradient / sqrt_mass
        vector = project_and_normalize(mass_weighted_gradient, rigid, modes)
        modes.append(vector)
        cartesian_unit_q = vector.reshape(12, 3) / sqrt_mass
        mode_rows.append(
            {
                "mode_id": name,
                "irrep": irrep,
                "construction": "mass-weighted internal-coordinate gradient with rigid-body projection",
                "mass_weighted_vector": rounded_matrix(vector),
                "cartesian_displacement_per_unit_Q": np.round(cartesian_unit_q, 14).tolist(),
            }
        )

    matrix = np.column_stack(modes)
    gram = matrix.T @ matrix
    rigid_overlap = rigid.T @ matrix
    c6_b2u = float(np.dot(modes[0], c6_transform(modes[0])))
    c6_a1g = float(np.dot(modes[1], c6_transform(modes[1])))
    inversion_b2u = float(np.dot(modes[0], inversion_transform(modes[0])))
    inversion_a1g = float(np.dot(modes[1], inversion_transform(modes[1])))
    e2g = np.column_stack(modes[2:4])
    transformed_e2g = np.column_stack([c6_transform(modes[2]), c6_transform(modes[3])])
    e2g_representation = e2g.T @ transformed_e2g
    e2g_residual = float(np.linalg.norm(transformed_e2g - e2g @ e2g_representation))
    inversion_e2g = e2g.T @ np.column_stack(
        [inversion_transform(modes[2]), inversion_transform(modes[3])]
    )

    tolerances = {
        "normalization": 1.0e-10,
        "orthogonality": 1.0e-10,
        "rigid_body_overlap": 1.0e-9,
        "one_dimensional_character": 1.0e-8,
        "e2g_trace": 1.0e-8,
        "e2g_determinant": 1.0e-8,
        "e2g_subspace_residual": 1.0e-8,
    }
    checks = {
        "all_modes_normalized": bool(np.max(np.abs(np.diag(gram) - 1.0)) <= tolerances["normalization"]),
        "all_modes_orthogonal": bool(np.max(np.abs(gram - np.eye(4))) <= tolerances["orthogonality"]),
        "translations_rotations_projected": bool(np.max(np.abs(rigid_overlap)) <= tolerances["rigid_body_overlap"]),
        "B2u_C6_character_minus_one": abs(c6_b2u + 1.0) <= tolerances["one_dimensional_character"],
        "B2u_inversion_ungerade": abs(inversion_b2u + 1.0) <= tolerances["one_dimensional_character"],
        "A1g_C6_character_plus_one": abs(c6_a1g - 1.0) <= tolerances["one_dimensional_character"],
        "A1g_inversion_gerade": abs(inversion_a1g - 1.0) <= tolerances["one_dimensional_character"],
        "E2g_C6_trace_minus_one": abs(float(np.trace(e2g_representation)) + 1.0) <= tolerances["e2g_trace"],
        "E2g_C6_determinant_plus_one": abs(float(np.linalg.det(e2g_representation)) - 1.0) <= tolerances["e2g_determinant"],
        "E2g_subspace_closed": e2g_residual <= tolerances["e2g_subspace_residual"],
        "E2g_inversion_gerade": bool(np.max(np.abs(inversion_e2g - np.eye(2))) <= tolerances["one_dimensional_character"]),
    }

    result = {
        "schema_version": "1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scientific_energy_calculation": False,
        "geometry_source": str(args.geometry.relative_to(ROOT)).replace("\\", "/"),
        "geometry_file_sha256": sha256(args.geometry),
        "geometry_contract_sha256": geometry_contract_hash,
        "atomic_masses_u": MASSES,
        "coordinate_kind": "symmetry_adapted_skeletal_seed_not_hessian_eigenmode",
        "modes": mode_rows,
        "diagnostics": {
            "gram_matrix": np.round(gram, 14).tolist(),
            "maximum_rigid_body_overlap": float(np.max(np.abs(rigid_overlap))),
            "B2u_C6_character": c6_b2u,
            "B2u_inversion_character": inversion_b2u,
            "A1g_C6_character": c6_a1g,
            "A1g_inversion_character": inversion_a1g,
            "E2g_C6_representation": np.round(e2g_representation, 14).tolist(),
            "E2g_C6_trace": float(np.trace(e2g_representation)),
            "E2g_C6_determinant": float(np.linalg.det(e2g_representation)),
            "E2g_subspace_residual": e2g_residual,
            "E2g_inversion_representation": np.round(inversion_e2g, 14).tolist(),
        },
        "tolerances": tolerances,
        "checks": checks,
        "displacement_protocol": {
            "amplitude_definition": "For each seed, rescale its Cartesian displacement so that the largest atomic displacement equals the requested amplitude in angstrom.",
            "signed_max_cartesian_displacement_angstrom": [-0.02, -0.01, -0.005, -0.0025, 0.0, 0.0025, 0.005, 0.01, 0.02],
            "primary_fit_window_angstrom": [-0.01, 0.01],
            "outer_points_role": "step-size and anharmonicity sensitivity only",
            "positive_negative_pairs_required": True,
        },
        "geometry_constraints": {
            "center_of_mass": "recenter to the frozen reference center of mass after every displacement",
            "planarity": "all z coordinates fixed at the reference-plane value",
            "relaxation": "none for the primary seed path",
            "orthogonal_coordinates": "all components orthogonal to the selected seed/subspace are fixed to zero",
            "hydrogen_rule": "hydrogens follow the generated seed vector; no separate manual C-H adjustment",
        },
        "hessian_comparison_rule_for_gate_v2_3": {
            "authorization_at_seed_generation": "NOT_AUTHORIZED_AT_GATE_V2_0",
            "current_authorization_record": "configs/science_v0.2/wp_authorizations.json",
            "one_dimensional_irreps": "compare absolute mass-weighted vector overlap after rigid-body projection; sign is arbitrary",
            "degenerate_or_near_degenerate_irreps": "compare subspaces using singular values/principal angles; never require vector-by-vector identity",
            "minimum_accepted_overlap_or_singular_value": 0.90,
            "mismatch_action": "retain the preregistered seed and its results as SEED_PATH; report the Hessian eigensubspace separately; do not replace or rotate the original seed post hoc",
        },
        "boundary": "These vectors freeze displacement subspaces only. A method-specific Hessian is still required after WP3 authorization to identify normal-mode mixing and curvatures.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
