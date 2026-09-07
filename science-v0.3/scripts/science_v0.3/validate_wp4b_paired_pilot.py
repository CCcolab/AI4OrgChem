from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project
    contract = load(project / "configs/science_v0.3/wp4b_paired_pilot_contract.json")
    manifest = load(project / "data/science_v0.3/inputs/wp4b/input_manifest.json")
    anchors = load(project / "configs/science_v0.3/wp4b_source_0k_anchors.json")
    assert contract["status"] == "FROZEN_FOR_PAIRED_PILOT"
    assert contract["changes_existing_p12_a_result"] is False
    assert contract["estimand"]["relation_to_p12_a"] == "INCOMPARABLE"
    assert len(manifest["records"]) == 24
    assert {int(row["N"]) for row in manifest["records"]} == {8, 10, 16, 18, 32, 34}
    for n in (8, 10, 16, 18, 32, 34):
        rows = [row for row in manifest["records"] if int(row["N"]) == n]
        assert {row["species"] for row in rows} == set("ABCD")
        for row in rows:
            assert row["primary"]["sha256"] and row["secondary"]["sha256"]
            assert row["primary"]["ez_sequence"] and row["secondary"]["ez_sequence"]
    assert len(anchors["records"]) == 16

    summary_path = project / "data/science_v0.3/processed/wp4b/wp4b_paired_pilot_summary.json"
    decision_path = project / "data/science_v0.3/decisions/wp4b/gate_v2_4p_decision.json"
    if summary_path.exists() and decision_path.exists():
        summary, decision = load(summary_path), load(decision_path)
        assert summary["gate_status"] == decision["status"]
        coverage = summary["candidate_evaluation_coverage"]
        expected_status = "PASSED" if all(item["pass"] for item in decision["criteria"].values()) else "IN_PROGRESS_NOT_PASSED"
        assert decision["status"] == expected_status
        assert len(coverage) == 24
        assert decision["criteria"]["both_conformer_sources_actually_evaluated"]["pass"] == all(
            row["both_sources_evaluated"] for row in coverage
        )
        if decision["status"] == "PASSED":
            assert len(summary["six_point_results"]) == 6
            assert all(item["pass"] for item in decision["criteria"].values())
            assert decision["decision"] == "ELIGIBLE_FOR_SEPARATE_EXPANSION_APPROVAL"
            by_n = {int(row["N"]): row for row in summary["six_point_results"]}
            assert by_n[10]["classification"] == "antiaromatic"
            assert by_n[10]["boundary_sensitive_within_0_1_kcal_mol"] is True
            assert by_n[32]["classification"] == "nonaromatic_interval"
            for row in summary["small_conformer_selection"]["selected"]:
                result_path = project / "data/science_v0.3/raw/wp4b" / f"{row['id']}.json"
                if not result_path.exists() and row["id"].endswith("_source") and int(row["N"]) >= 16:
                    anchor = next(
                        item for item in anchors["records"]
                        if int(item["N"]) == int(row["N"]) and item["species"] == row["species"]
                    )
                    # Published source anchors store E_electronic and E_0.
                    # Their ZPVE is therefore a derived quantity rather than a
                    # separately serialized field in the frozen anchor schema.
                    zpve = float(anchor["e0_hartree"]) - float(anchor["electronic_hartree"])
                    # ZPVE is extensive; a molecule-size-independent 0.5 Eh
                    # ceiling is invalid for the N=32/34 source systems.
                    assert zpve > 0.0
                    assert abs(float(anchor["e0_hartree"]) - float(anchor["electronic_hartree"]) - zpve) < 1e-10
                    continue
                result = load(result_path)
                assert result["schema_version"] in {
                    "science-v0.3-wp4b-small-dft-result-1",
                    "science-v0.3-wp4b-dft-result-2",
                }
                assert result["minimum"] is True
                assert 0.0 < float(result["zpve_hartree"]) < 0.5
                assert abs(float(result["e0_hartree"]) - float(result["electronic_hartree"]) - float(result["zpve_hartree"])) < 1e-10
        else:
            assert decision["decision"] == "DO_NOT_EXPAND"

    forbidden = {"SC-016-D4SC08225G-s001.pdf", "SC-016-D4SC08225G-s002.zip"}
    found = []
    for path in project.rglob("*"):
        # Windows may expose stale or self-referential reparse points in the
        # workspace.  They are not release files and must not prevent the
        # archive-name scan from checking every accessible regular file.
        try:
            if path.name in forbidden and path.is_file():
                found.append(str(path))
        except OSError:
            continue
    assert not found, f"Third-party source archives must remain outside the repository: {found}"
    print("WP4B_VALIDATION_OK")


if __name__ == "__main__":
    main()
