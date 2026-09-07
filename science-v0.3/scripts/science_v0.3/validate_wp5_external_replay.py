from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    decision = load(project / "data/science_v0.3/decisions/wp5/gate_v2_5_decision.json")
    assert decision["status"] == "PASSED"
    assert decision["replay_status"] == "EXTERNAL_CLEAN_REPLAY"
    assert decision["agent_maturity"] == "M2"
    assert decision["external_replayer"] is True
    assert decision["bundle_only_filesystem"] is True
    assert decision["network_unshared_during_quantum_calculation"] is True
    assert decision["scientific_grade_modified"] is False
    assert decision["comparison_pass"] is True
    assert decision["redaction_pass"] is True
    assert float(decision["absolute_difference_hartree"]) <= float(decision["tolerance_hartree"])
    bundle_path = project / decision["run_bundle"]
    bundle = load(bundle_path)
    schema = load(project / "configs/science_v0.2/agent_run_bundle.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(bundle), key=lambda item: list(item.path))
    assert not errors, [error.message for error in errors]
    result_artifact = next(row for row in bundle["evidence_graph"] if row["role"] == "pre_unblind_quantum_result")
    assert sha(project / result_artifact["path"]) == decision["result_sha256_frozen_before_unblinding"]
    print("WP5_EXTERNAL_REPLAY_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
