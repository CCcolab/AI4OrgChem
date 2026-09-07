from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def active_script(fragment: str) -> bool:
    proc = Path("/proc")
    if not proc.exists():
        return False
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if fragment in command and "supervise_wp4b_closure.py" not in command:
            return True
    return False


def valid_summary(path: Path, field: str) -> bool:
    if not path.exists():
        return False
    try:
        return bool(json.loads(path.read_text(encoding="utf-8")).get(field))
    except (json.JSONDecodeError, OSError):
        return False


def run(command: list[str], project: Path) -> None:
    completed = subprocess.run(command, cwd=project, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {command}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args()
    project = args.project.resolve()
    scripts = project / "scripts/science_v0.3"
    raw = project / "data/science_v0.3/raw/wp4b"
    status_path = raw / "wp4b_supervisor_status.json"

    def status(value: str, **extra: object) -> None:
        payload = {"schema_version": "science-v0.3-wp4b-supervisor-1", "status": value, "updated_utc": datetime.now(timezone.utc).isoformat(), **extra}
        status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status("WAITING_FOR_ACTIVE_PREFLIGHT")
    while active_script("run_wp4b_crest_fallback.py") or active_script("run_wp4b_selected_hessians.py"):
        time.sleep(args.poll_seconds)

    crest_summary = raw / "crest_fallback_summary.json"
    if not valid_summary(crest_summary, "all_triggered_targets_completed"):
        status("RUNNING_CREST_FALLBACK")
        run([sys.executable, str(scripts / "run_wp4b_crest_fallback.py"), "--project", str(project), "--threads", "8"], project)

    small_selection = raw / "small_conformer_selection.json"
    small_hessian = raw / "auditbest_small_hessian_batch.json"
    if not small_hessian.exists():
        status("RUNNING_SMALL_SELECTED_HESSIANS")
        run([sys.executable, str(scripts / "run_wp4b_selected_hessians.py"), "--project", str(project), "--workers", "2", "--threads-per-job", "4", "--selection-name", small_selection.name, "--summary-name", small_hessian.name], project)

    status("RUNNING_CLOSURE_PIPELINE")
    completed = subprocess.run(
        [sys.executable, str(scripts / "run_wp4b_closure_pipeline.py"), "--project", str(project), "--workers", "2", "--threads-per-job", "4"],
        cwd=project,
        check=False,
    )
    status("COMPLETED" if completed.returncode == 0 else "FAILED", returncode=completed.returncode)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
