from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--threads-per-job", type=int, default=4)
    args = parser.parse_args()
    project = args.project.resolve()
    script_root = project / "scripts/science_v0.3"
    raw = project / "data/science_v0.3/raw/wp4b"
    state_path = raw / "wp4b_closure_pipeline_state.json"
    crest_summary_path = raw / "crest_fallback_summary.json"
    crest_summary = json.loads(crest_summary_path.read_text(encoding="utf-8"))
    if not crest_summary.get("all_triggered_targets_completed"):
        raise RuntimeError("CREST fallback must finish before the DFT closure pipeline")

    python = sys.executable
    stages = [
        (
            "medium_auditbest_dft",
            [python, str(script_root / "run_wp4b_small_batch.py"), "--project", str(project), "--n-values", "16,18", "--sources", "etkdg,auditbest", "--workers", str(args.workers), "--threads-per-job", str(args.threads_per_job), "--summary-name", "etkdg_auditbest_medium_batch.json"],
        ),
        (
            "large_auditbest_dft",
            [python, str(script_root / "run_wp4b_small_batch.py"), "--project", str(project), "--n-values", "32,34", "--sources", "etkdg,auditbest", "--workers", str(args.workers), "--threads-per-job", str(args.threads_per_job), "--summary-name", "etkdg_auditbest_large_batch.json"],
        ),
        (
            "crest_best_dft",
            [python, str(script_root / "run_wp4b_small_batch.py"), "--project", str(project), "--n-values", "18,32", "--sources", "crest", "--workers", str(args.workers), "--threads-per-job", str(args.threads_per_job), "--summary-name", "crest_best_dft_batch.json"],
        ),
        (
            "paired_selection",
            [python, str(script_root / "select_wp4b_small_minima.py"), "--project", str(project), "--n-values", "8,10,16,18,32,34", "--secondary-sources", "etkdg,auditbest,crest"],
        ),
        (
            "selected_hessians",
            [python, str(script_root / "run_wp4b_selected_hessians.py"), "--project", str(project), "--workers", str(args.workers), "--threads-per-job", str(args.threads_per_job), "--selection-name", "paired_conformer_selection.json", "--summary-name", "paired_selected_hessian_batch.json"],
        ),
        (
            "gate_summary",
            [python, str(script_root / "summarize_wp4b_paired_pilot.py"), "--project", str(project)],
        ),
        (
            "gate_validation",
            [python, str(script_root / "validate_wp4b_paired_pilot.py"), "--project", str(project)],
        ),
    ]
    state = {
        "schema_version": "science-v0.3-wp4b-closure-pipeline-state-1",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "stages": [],
    }
    for name, command in stages:
        stage = {"name": name, "status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(), "command": command}
        state["stages"].append(stage)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(command, cwd=project, check=False)
        stage["returncode"] = completed.returncode
        stage["finished_utc"] = datetime.now(timezone.utc).isoformat()
        stage["status"] = "COMPLETED" if completed.returncode == 0 else "FAILED"
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if completed.returncode != 0:
            state["status"] = "FAILED"
            state["failed_stage"] = name
            state["finished_utc"] = datetime.now(timezone.utc).isoformat()
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return completed.returncode
    decision = json.loads((project / "data/science_v0.3/decisions/wp4b/gate_v2_4p_decision.json").read_text(encoding="utf-8"))
    state["status"] = "COMPLETED" if decision["status"] == "PASSED" else "COMPLETED_GATE_NOT_PASSED"
    state["gate_status"] = decision["status"]
    state["finished_utc"] = datetime.now(timezone.utc).isoformat()
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if decision["status"] == "PASSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
