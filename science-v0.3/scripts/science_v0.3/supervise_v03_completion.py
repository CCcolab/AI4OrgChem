from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--replay-python", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=60)
    args = parser.parse_args()
    project = args.project.resolve()
    scripts = project / "scripts/science_v0.3"
    status_path = project / "runs/science_v0.3/v03_completion_supervisor.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)

    state: dict[str, object] = {
        "schema_version": "science-v0.3-completion-supervisor-1",
        "status": "WAITING_FOR_GATE_V2_4P",
        "started_utc": now(),
        "stages": [],
    }

    def save() -> None:
        state["updated_utc"] = now()
        status_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    save()
    wp4b_decision = project / "data/science_v0.3/decisions/wp4b/gate_v2_4p_decision.json"
    wp4b_supervisor = project / "data/science_v0.3/raw/wp4b/wp4b_supervisor_status.json"
    wp4b_closure = project / "data/science_v0.3/raw/wp4b/wp4b_closure_pipeline_state.json"
    while True:
        decision = load(wp4b_decision)
        if decision and decision.get("status") == "PASSED":
            break
        upstream = load(wp4b_supervisor)
        if upstream and upstream.get("status") == "FAILED":
            closure = load(wp4b_closure)
            if closure and closure.get("status") == "RUNNING":
                if state.get("status") != "WAITING_FOR_RECOVERED_GATE_V2_4P":
                    state["status"] = "WAITING_FOR_RECOVERED_GATE_V2_4P"
                    state["stale_failed_upstream"] = upstream
                    state["active_recovery"] = {
                        "status": closure.get("status"),
                        "started_utc": closure.get("started_utc"),
                        "state_file": str(wp4b_closure.relative_to(project)),
                    }
                    save()
                time.sleep(args.poll_seconds)
                continue
            state["status"] = "BLOCKED_BY_WP4B_FAILURE"
            state["upstream"] = upstream
            state["closure"] = closure
            save()
            return 2
        time.sleep(args.poll_seconds)

    stages = [
        (
            "wp5_external_replay",
            [sys.executable, str(scripts / "run_wp5_external_replay.py"), "--project", str(project), "--replay-python", str(args.replay_python)],
        ),
        (
            "wp5_validation",
            [sys.executable, str(scripts / "validate_wp5_external_replay.py"), "--project", str(project)],
        ),
        (
            "wp6_finalize",
            [sys.executable, str(scripts / "finalize_v03_release.py"), "--project", str(project)],
        ),
        (
            "wp6_build_staging",
            [sys.executable, str(scripts / "prepare_github_v03_release.py"), "--project", str(project)],
        ),
        (
            "wp6_validate_staging_pre_final",
            [sys.executable, str(scripts / "validate_github_v03_release.py"), "--project", str(project)],
        ),
        (
            "wp6_complete_release",
            [sys.executable, str(scripts / "complete_v03_release.py"), "--project", str(project)],
        ),
        (
            "wp6_validate_staging_final",
            [sys.executable, str(scripts / "validate_github_v03_release.py"), "--project", str(project)],
        ),
    ]
    state["status"] = "RUNNING_POST_WP4B"
    save()
    for name, command in stages:
        row = {"name": name, "status": "RUNNING", "started_utc": now(), "command": command}
        state["stages"].append(row)
        save()
        completed = subprocess.run(command, cwd=project, check=False)
        row.update({"returncode": completed.returncode, "finished_utc": now(), "status": "COMPLETED" if completed.returncode == 0 else "FAILED"})
        save()
        if completed.returncode != 0:
            state["status"] = "FAILED"
            state["failed_stage"] = name
            save()
            return completed.returncode
    state["status"] = "COMPLETED_V03_STAGING_VALIDATED"
    state["finished_utc"] = now()
    save()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
