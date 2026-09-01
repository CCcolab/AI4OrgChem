from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "development" / "science-v0.2"
PRIVATE_PATH = re.compile(r"[A-Za-z]:\\(?:Users|AI4Science)\\|/home/[A-Za-z0-9._-]+")
FORBIDDEN_SUFFIXES = {".pdf", ".epub", ".mobi", ".zip", ".gz", ".exe", ".dll", ".so"}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    required = [
        "README.md",
        "configs/wp0_gate.json",
        "configs/wp0_gate_final_decision.json",
        "configs/wp0_readiness.json",
        "configs/wp_authorizations.json",
        "configs/wp1_qp2_environment_smoke.public.json",
        "configs/wp2_core_anchors.json",
        "configs/wp3_symmetry_mode_seeds.json",
        "docs/protocols/WP1_WP4_EXECUTION_CONTRACTS.md",
        "docs/reports/WP0_IMPLEMENTATION_STATUS_2026-09-01.md",
        "docs/reports/GATE_V2_0_FINAL_DECISION_AND_WP1_WP3_AUTHORIZATION_2026-09-01.md",
        "docs/reports/WP0_QP22_CIPSI_ENVIRONMENT_2026-09-01.md",
        "reproducibility/ai4orgchem-v02-cipsi.environment.yml",
        "reproducibility/ai4orgchem-v02-cipsi.conda-explicit.txt",
    ]
    for relative in required:
        if not (SNAPSHOT / relative).is_file():
            failures.append(f"missing public WP0 artifact: {relative}")

    if not failures:
        gate = load_json(SNAPSHOT / "configs" / "wp0_gate.json")
        decision = load_json(SNAPSHOT / "configs" / "wp0_gate_final_decision.json")
        readiness = load_json(SNAPSHOT / "configs" / "wp0_readiness.json")
        authorizations = load_json(SNAPSHOT / "configs" / "wp_authorizations.json")
        smoke = load_json(SNAPSHOT / "configs" / "wp1_qp2_environment_smoke.public.json")
        if gate.get("status") != "PASSED" or decision.get("gate_status") != "PASSED":
            failures.append("Gate V2-0 final PASS records disagree")
        if readiness.get("science_jobs_started") is not False:
            failures.append("WP0 snapshot claims that science jobs started")
        if readiness.get("v0_1_mutated") is not False:
            failures.append("WP0 snapshot claims V0.1 mutation")
        if smoke.get("classification") != "ENVIRONMENT_AND_NON_CBD_TOY_SMOKE_ONLY":
            failures.append("QP smoke classification changed")
        if smoke.get("scientific_energy_calculation") is not False:
            failures.append("QP smoke is misclassified as scientific")
        if smoke.get("contains_cyclobutadiene_input") is not False:
            failures.append("public WP0 smoke unexpectedly contains CBD input")
        if smoke.get("authorization_scope") != "HISTORICAL_STATE_AT_SMOKE_EXECUTION":
            failures.append("public QP smoke record does not identify its historical authorization state")
        packages = authorizations.get("work_packages", {})
        if packages.get("WP1", {}).get("status") != "AUTHORIZED_TO_START":
            failures.append("WP1 current authorization record is missing")
        if packages.get("WP3", {}).get("status") != "AUTHORIZED_TO_START":
            failures.append("WP3 current authorization record is missing")
        if packages.get("WP1", {}).get("execution_started") is not False:
            failures.append("WP1 unexpectedly claims an executed science job")
        if packages.get("WP3", {}).get("execution_started") is not False:
            failures.append("WP3 unexpectedly claims an executed science job")
        if packages.get("WP2", {}).get("status") != "HOLD" or packages.get("WP4", {}).get("status") != "HOLD":
            failures.append("WP2/WP4 HOLD boundary changed")
        identity = smoke.get("implementation", {})
        if identity.get("requested_release") != "v2.2.2":
            failures.append("Quantum Package release identity changed")
        if identity.get("git_commit") != "0f320db735bfdbdf9861c9cad9f3f64175cc8c3c":
            failures.append("Quantum Package commit identity changed")
        if identity.get("source_internal_version") != "2.3.1":
            failures.append("Quantum Package internal VERSION identity changed")
        if {row.get("id") for row in smoke.get("smoke_tests", [])} != {"UPSTREAM_H2_1", "UPSTREAM_B_B"}:
            failures.append("public smoke fixture set changed")
        elif not all(row.get("status") == "PASS" for row in smoke["smoke_tests"]):
            failures.append("public smoke record contains a failed fixture")

    for path in SNAPSHOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(SNAPSHOT).as_posix()
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden binary/archive in WP0 snapshot: {relative}")
        if path.suffix.lower() in {".md", ".json", ".yml", ".yaml", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if PRIVATE_PATH.search(text):
                failures.append(f"private host path in WP0 snapshot: {relative}")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "snapshot": "development/science-v0.2",
        "gate_status": "PASSED",
        "science_jobs_started": False,
        "files_checked": sum(1 for path in SNAPSHOT.rglob("*") if path.is_file()),
        "failure_count": len(failures),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
