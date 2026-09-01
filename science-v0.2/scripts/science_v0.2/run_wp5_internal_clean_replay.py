from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "runs/science_v0.2/wp5_internal_clean_replay/replay_result.json"
EVALUATORS = [
    "scripts/science_v0.2/evaluate_wp1.py",
    "scripts/science_v0.2/evaluate_wp2.py",
    "scripts/science_v0.2/evaluate_wp3.py",
    "scripts/science_v0.2/evaluate_wp4_readiness.py",
]
INPUTS = [
    "configs/science_v0.2/claim_estimand_registry.json",
    "docs/releases/science_v0.2/protocols/WP1_WP4_EXECUTION_CONTRACTS.md",
    "data/science_v0.2/raw/wp1/wp1_endpoints.json",
    "data/science_v0.2/raw/wp1/wp1_cas4_path.json",
    "data/science_v0.2/raw/wp1/wp1_cas12_endpoints.json",
    "data/science_v0.2/processed/wp1/wp1_qp2_cipsi_result.json",
    "data/science_v0.2/raw/wp2/wp2_open_program_anchors.json",
    "data/science_v0.2/raw/wp3/wp3_hessian_mixing.json",
    "data/science_v0.2/raw/wp3/wp3_grid.json",
]
OUTPUTS = [
    "data/science_v0.2/decisions/wp1/gate_v2_1_decision.json",
    "data/science_v0.2/decisions/wp1/p09b_evidence_record.json",
    "docs/releases/science_v0.2/reports/WP1_GATE_V2_1_REPORT.md",
    "data/science_v0.2/decisions/wp2/gate_v2_2_decision.json",
    "docs/releases/science_v0.2/reports/WP2_GATE_V2_2_REPORT.md",
    "data/science_v0.2/decisions/wp3/gate_v2_3_decision.json",
    "data/science_v0.2/decisions/wp3/p10a_evidence_record.json",
    "data/science_v0.2/decisions/wp3/p10b_evidence_record.json",
    "docs/releases/science_v0.2/reports/WP3_GATE_V2_3_REPORT.md",
    "data/science_v0.2/decisions/wp4/gate_v2_4p_decision.json",
    "docs/releases/science_v0.2/reports/WP4_GATE_V2_4P_REPORT.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(root: Path, relative: str) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, destination)


def main() -> None:
    replay_root = ROOT / "runs/science_v0.2"
    replay_root.mkdir(parents=True, exist_ok=True)
    commands = []
    with tempfile.TemporaryDirectory(prefix="wp5-clean-", dir=replay_root) as temporary:
        clean = Path(temporary)
        for relative in EVALUATORS + INPUTS:
            copy(clean, relative)
        for relative in EVALUATORS:
            completed = subprocess.run(
                [sys.executable, str(clean / relative)],
                cwd=clean,
                text=True,
                capture_output=True,
                check=False,
            )
            commands.append(
                {
                    "command": f"{Path(sys.executable).name} {relative}",
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
                    "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
                }
            )
        comparisons = []
        for relative in OUTPUTS:
            original = ROOT / relative
            replayed = clean / relative
            comparisons.append(
                {
                    "path": relative,
                    "original_sha256": sha(original) if original.is_file() else None,
                    "replayed_sha256": sha(replayed) if replayed.is_file() else None,
                    "byte_identical": original.is_file() and replayed.is_file() and original.read_bytes() == replayed.read_bytes(),
                }
            )
    passed = all(row["exit_code"] == 0 for row in commands) and all(row["byte_identical"] for row in comparisons)
    result = {
        "schema_version": "science-v0.2-wp5-internal-clean-replay-1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "replay_status": "INTERNAL_CLEAN_REPLAY" if passed else "NOT_REPLAYED",
        "agent_maturity": "M1_PLUS",
        "external_replayer": False,
        "fresh_temporary_workspace": True,
        "scientific_calculations_rerun": False,
        "scope": "Deterministic regeneration of WP1-WP4 decisions and reports from frozen machine results.",
        "commands": commands,
        "artifact_comparisons": comparisons,
        "pass": passed,
        "boundary": "This replay verifies deterministic evidence assembly, not independent recomputation of the underlying quantum-chemistry wavefunctions; it therefore does not qualify as EXTERNAL_CLEAN_REPLAY or M2.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pass": passed, "replay_status": result["replay_status"], "artifacts": len(comparisons)}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
