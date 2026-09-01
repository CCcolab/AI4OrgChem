"""Strictly validate and deterministically rebuild the public P14 decision."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
P14 = ROOT / "evidence/P01-P14/P14"
RESULT = P14 / "result.json"
SCHEMA = ROOT / "software/schemas/p14-result.schema.json"
CLASSIFIER_DIR = ROOT / "software/scripts"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_xyz(path: Path) -> list[list[Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    count = int(lines[0])
    atoms = []
    for line in lines[2:]:
        if line.strip():
            symbol, x, y, z = line.split()
            atoms.append([symbol, float(x), float(y), float(z)])
    if len(atoms) != count:
        raise ValueError(f"{path}: XYZ count {count} but parsed {len(atoms)} atoms")
    return atoms


def compare_atoms(label: str, xyz: list[list[Any]], reference: list[list[Any]], failures: list[str]) -> None:
    if len(xyz) != len(reference):
        failures.append(f"{label}: atom counts differ")
        return
    for index, (actual, expected) in enumerate(zip(xyz, reference, strict=True), start=1):
        if actual[0] != expected[0]:
            failures.append(f"{label}: atom {index} element differs")
        for axis, (left, right) in enumerate(zip(actual[1:], expected[1:], strict=True)):
            if not math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1.0e-11):
                failures.append(f"{label}: atom {index} axis {axis} differs")


def safe_root_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"path escapes repository: {relative}")
    return path


def main() -> int:
    failures: list[str] = []
    try:
        result = load_json(RESULT)
        schema = load_json(SCHEMA)
    except (json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "failures": [str(exc)]}, indent=2))
        return 1

    for error in sorted(Draft202012Validator(schema).iter_errors(result), key=lambda item: list(item.path)):
        failures.append(f"schema: {'/'.join(map(str, error.path))}: {error.message}")

    evidence_paths: list[Path] = []
    for relative in result.get("evidence_files", []):
        try:
            path = safe_root_path(relative)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        evidence_paths.append(path)
        if not path.is_file():
            failures.append(f"missing evidence file: {relative}")
            continue
        try:
            load_json(path)
        except (json.JSONDecodeError, ValueError) as exc:
            failures.append(f"{relative}: {exc}")
        if result.get("evidence_sha256", {}).get(relative) != digest(path):
            failures.append(f"evidence hash mismatch: {relative}")

    input_paths: dict[str, Path] = {}
    for name, relative in result.get("input_files", {}).items():
        try:
            path = safe_root_path(relative)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        input_paths[name] = path
        if not path.is_file():
            failures.append(f"missing input file: {relative}")
        elif result.get("input_sha256", {}).get(name) != digest(path):
            failures.append(f"input hash mismatch: {relative}")

    if len(evidence_paths) == 4 and all(path.is_file() for path in evidence_paths):
        smoke, pilot, equivalence, source_level = map(load_json, evidence_paths)
        if pilot.get("method", {}).get("engine") != "PySCF_plus_SciPy":
            failures.append("pilot engine identity missing or changed")
        if source_level.get("method", {}).get("engine") != "PySCF":
            failures.append("source-level engine identity missing or changed")
        if source_level.get("method", {}).get("basis") != "6-31g(d)":
            failures.append("source-level basis identity missing or changed")

        if "source_proxy_G" in input_paths and input_paths["source_proxy_G"].is_file():
            compare_atoms(
                "source_proxy_G",
                parse_xyz(input_paths["source_proxy_G"]),
                source_level["geometry_contract"]["G"]["atoms_angstrom"],
                failures,
            )
        if "source_proxy_PLG" in input_paths and input_paths["source_proxy_PLG"].is_file():
            compare_atoms(
                "source_proxy_PLG",
                parse_xyz(input_paths["source_proxy_PLG"]),
                source_level["geometry_contract"]["PLG"]["atoms_angstrom"],
                failures,
            )

        sys.path.insert(0, str(CLASSIFIER_DIR))
        from classify_p14_strained_aromatic_pi_distortivity import run  # noqa: PLC0415

        rebuilt = run(
            ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml",
            *evidence_paths,
        )
        for field in (
            "classification",
            "quantitative_evidence",
            "decision_checks",
            "decision_verdict",
            "evidence_files",
            "evidence_sha256",
            "input_files",
            "input_sha256",
            "geometry_sha256",
        ):
            if rebuilt.get(field) != result.get(field):
                failures.append(f"deterministic rebuild mismatch: {field}")
        if not all(result.get("decision_checks", {}).values()):
            failures.append("one or more P14 decision checks are false")

    summary = {
        "status": "PASS" if not failures else "FAIL",
        "evidence_files_checked": len(evidence_paths),
        "input_files_checked": len(input_paths),
        "schema": "Draft 2020-12",
        "deterministic_decision_rebuild": not failures,
        "expensive_qm_rerun": False,
        "failures": failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
