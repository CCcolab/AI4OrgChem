from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "science-v0.2"
PRIVATE_PATH = re.compile(r"[A-Za-z]:\\(?:Users|AI4Science)\\|/home/[A-Za-z0-9._-]+|/mnt/[a-z]/AI4Science", re.I)
FORBIDDEN_SUFFIXES = {".pdf", ".epub", ".mobi", ".zip", ".gz", ".exe", ".dll", ".so", ".log", ".out", ".wfn", ".wfx", ".chk", ".gbw"}


def load(relative: str) -> dict:
    return json.loads((SNAPSHOT / relative).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    required = [
        "README.md", "sha256-manifest.json",
        "configs/science_v0.2/v0.1_baseline.json",
        "configs/science_v0.2/v0.2_release_status.json",
        "configs/science_v0.2/wp_authorizations.json",
        "data/science_v0.2/decisions/wp1/gate_v2_1_decision.json",
        "data/science_v0.2/decisions/wp2/gate_v2_2_decision.json",
        "data/science_v0.2/decisions/wp3/gate_v2_3_decision.json",
        "data/science_v0.2/decisions/wp4/gate_v2_4p_decision.json",
        "runs/science_v0.2/wp5_internal_clean_replay/replay_result.json",
        "docs/releases/science_v0.2/V0.2_RELEASE_NOTES.md",
        "tests/science_v0.2/test_v02_release_contract.py",
    ]
    for relative in required:
        if not (SNAPSHOT / relative).is_file():
            failures.append(f"missing V0.2 artifact: {relative}")

    if not failures:
        status = load("configs/science_v0.2/v0.2_release_status.json")
        wp1 = load("data/science_v0.2/decisions/wp1/gate_v2_1_decision.json")
        wp2 = load("data/science_v0.2/decisions/wp2/gate_v2_2_decision.json")
        wp3 = load("data/science_v0.2/decisions/wp3/gate_v2_3_decision.json")
        wp4 = load("data/science_v0.2/decisions/wp4/gate_v2_4p_decision.json")
        replay = load("runs/science_v0.2/wp5_internal_clean_replay/replay_result.json")
        if status.get("version") != "0.2.0" or status.get("status") != "RELEASE_PACKAGE_READY":
            failures.append("V0.2 machine release status is not ready")
        if status.get("v0_1_p01_p14_mutated") is not False:
            failures.append("V0.2 claims that V0.1 was mutated")
        if wp1.get("gate_status") != "PASS_WITH_METHOD_SENSITIVITY":
            failures.append("WP1 status changed")
        if wp2.get("open_program_lane") != "FAIL" or wp2.get("psi4_backend_contract") != "FAIL" or wp2.get("gate_status") != "NOT_PASSED" or wp2.get("orca_available") is not False:
            failures.append("WP2 backend/ORCA boundary is misstated")
        if wp3.get("gate_status") != "PASS" or wp3.get("p10b_grade") != "R3":
            failures.append("WP3 result changed")
        if wp4.get("gate_status") != "NOT_PASSED" or wp4.get("scientific_calculation_started") is not False:
            failures.append("WP4 unresolved input boundary is misstated")
        if replay.get("replay_status") != "INTERNAL_CLEAN_REPLAY" or replay.get("agent_maturity") != "M1_PLUS":
            failures.append("WP5 replay/maturity axes changed")

        manifest = load("sha256-manifest.json")
        for row in manifest.get("files", []):
            path = SNAPSHOT / row["path"]
            if not path.is_file() or sha(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
                failures.append(f"manifest mismatch: {row['path']}")

    files_checked = 0
    for path in SNAPSHOT.rglob("*"):
        if not path.is_file():
            continue
        files_checked += 1
        relative = path.relative_to(SNAPSHOT).as_posix()
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden binary/log/archive: {relative}")
        if path.suffix.lower() in {".md", ".json", ".jsonl", ".yml", ".yaml", ".txt", ".py"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if PRIVATE_PATH.search(text):
                failures.append(f"private host path: {relative}")

    for readme in ("README.md", "README_zh-CN.md"):
        text = (ROOT / readme).read_text(encoding="utf-8")
        if "v0.2.0" not in text or "science-v0.2" not in text:
            failures.append(f"{readme} does not expose V0.2")

    result = {"status": "PASS" if not failures else "FAIL", "snapshot": "science-v0.2", "files_checked": files_checked, "failure_count": len(failures), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
