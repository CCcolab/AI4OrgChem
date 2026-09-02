from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "runs/science_v0.3/wp2/open_three_program"
SUMMARY = ROOT / "data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json"
DECISION = ROOT / "data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json"
CONTRACT = ROOT / "configs/science_v0.3/wp2_open_three_program_contract.json"
PUBLISHED_ANCHOR_ROOT = ROOT / "data/science_v0.3/raw/wp2/anchors"
HARTREE_TO_KCAL_MOL = 627.5094740631

ANCHORS = [
    "WP2-P03-NBA-000-EF",
    "WP2-P03-NBA-060-E",
    "WP2-P08-BUTADIENE-G-EG",
    "WP2-P09-BENZENE-G-E",
    "WP2-P09-CBD-G-E",
    "WP2-P10-BENZENE-B2U-Q0-EF",
    "WP2-P10-BENZENE-B2U-QPLUS-E",
    "WP2-P11-FURAN-G-E",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_result(anchor: str) -> tuple[Path, dict[str, Any]]:
    path = RUN_ROOT / anchor / "result.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def relative_pair(
    results: dict[str, dict[str, Any]], name: str, first: str, second: str
) -> dict[str, Any]:
    values = {}
    for program in ["PySCF", "Psi4", "NWChem"]:
        difference_hartree = (
            results[second]["programs"][program]["energy_hartree"]
            - results[first]["programs"][program]["energy_hartree"]
        )
        values[program] = difference_hartree * HARTREE_TO_KCAL_MOL
    span = max(values.values()) - min(values.values())
    return {
        "pair_id": name,
        "definition": f"{second} minus {first}",
        "values_kcal_mol": values,
        "cross_program_span_kcal_mol": span,
        "threshold_kcal_mol": 0.05,
        "pass": span <= 0.05,
    }


def main() -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    paths_and_rows = [load_result(anchor) for anchor in ANCHORS]
    results = {row["anchor_id"]: row for _, row in paths_and_rows}
    anchor_summary = []
    for path, row in paths_and_rows:
        published_path = PUBLISHED_ANCHOR_ROOT / f"{row['anchor_id']}.json"
        published_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, published_path)
        anchor_summary.append(
            {
                "anchor_id": row["anchor_id"],
                "result": str(published_path.relative_to(ROOT)).replace("\\", "/"),
                "result_sha256": sha256(published_path),
                "local_run_source": str(path.relative_to(ROOT)).replace("\\", "/"),
                "program_count": row["comparison"].get("program_count", len(row["programs"])),
                "energy_span_hartree": row["comparison"]["pairwise_span_hartree"],
                "gradient_pairwise_rms_hartree_per_bohr": row["comparison"].get(
                    "gradient_pairwise_rms_hartree_per_bohr"
                ),
                "projected_derivative_span_hartree_per_bohr": row["comparison"].get(
                    "projected_derivative_span_hartree_per_bohr"
                ),
                "pass": row["comparison"]["pass"],
            }
        )

    relative_pairs = [
        relative_pair(results, "P03_60_MINUS_0", "WP2-P03-NBA-000-EF", "WP2-P03-NBA-060-E"),
        relative_pair(
            results,
            "P10_QPLUS_MINUS_Q0",
            "WP2-P10-BENZENE-B2U-Q0-EF",
            "WP2-P10-BENZENE-B2U-QPLUS-E",
        ),
    ]
    anchors_pass = len(anchor_summary) == 8 and all(row["pass"] for row in anchor_summary)
    relative_pass = all(row["pass"] for row in relative_pairs)
    open_lane_pass = anchors_pass and relative_pass
    summary = {
        "schema_version": "science-v0.3-wp2-open-three-program-summary-1",
        "timestamp_utc": timestamp,
        "contract": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "contract_sha256": sha256(CONTRACT),
        "programs": {
            "PySCF": "2.14.0",
            "Psi4": "1.11",
            "NWChem": {"banner_version": "7.3.0", "revision": "3272822"},
        },
        "anchor_count": len(anchor_summary),
        "anchors": anchor_summary,
        "relative_energy_pairs": relative_pairs,
        "maximum_absolute_energy_span_hartree": max(
            row["energy_span_hartree"] for row in anchor_summary
        ),
        "maximum_gradient_pairwise_rms_hartree_per_bohr": max(
            value
            for row in anchor_summary
            for value in (row["gradient_pairwise_rms_hartree_per_bohr"] or {}).values()
        ),
        "maximum_projected_derivative_span_hartree_per_bohr": max(
            row["projected_derivative_span_hartree_per_bohr"] or 0.0 for row in anchor_summary
        ),
        "anchors_pass": anchors_pass,
        "relative_energy_pairs_pass": relative_pass,
        "open_three_program_lane_pass": open_lane_pass,
        "original_orca_lane_status": "NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE",
        "science_target_values_used_for_tuning": False,
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    decision = {
        "schema_version": "science-v0.3-gate-v2-2-open-lane-decision-1",
        "timestamp_utc": timestamp,
        "gate": "Gate V2-2",
        "work_package": "WP2",
        "status": "PASSED_OPEN_THREE_PROGRAM" if open_lane_pass else "NOT_PASSED",
        "scientific_question_status": "RESOLVED_WITHIN_FROZEN_OPEN_THREE_PROGRAM_ESTIMAND"
        if open_lane_pass
        else "UNRESOLVED",
        "summary": str(SUMMARY.relative_to(ROOT)).replace("\\", "/"),
        "summary_sha256": sha256(SUMMARY),
        "decision_basis": {
            "eight_of_eight_core_anchors_pass": anchors_pass,
            "two_of_two_relative_energy_pairs_pass": relative_pass,
            "functional_identity_aligned": True,
            "frozen_bohr_geometries": True,
            "high_grid_convergence_aligned": True,
            "density_fitting_disabled": True,
            "exact_direct_integrals": True,
        },
        "scope_statement": "This closes the scientific cross-program reproducibility question with PySCF, Psi4, and NWChem. It does not claim that NWChem is ORCA or that the original ORCA-specific lane has been executed.",
        "original_orca_lane_status": "NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE",
        "effect_on_v0_1_fourteen_propositions": "NO_CHANGE; WP2 raises independent reproducibility evidence only.",
        "effect_on_v0_2_release": "NO_MUTATION; v0.2.0 remains immutable.",
    }
    DECISION.parent.mkdir(parents=True, exist_ok=True)
    DECISION.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary["open_three_program_lane_pass"], "gate": decision["status"]}, indent=2))


if __name__ == "__main__":
    main()
