from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROVIDERS = (
    ("DeepSeek", "deepseek-v4-flash", "https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    ("MiniMax", "MiniMax-M3.0", "https://api.minimax.io/v1", "MINIMAX_API_KEY"),
    ("MiniMax", "MiniMax-M3.0", "https://api.minimaxi.com/v1", "MINIMAX_CN_API_KEY"),
    ("Qwen", "qwen-plus", "https://dashscope.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        value = value.strip().strip("\"'")
        values[key] = value
    return values


def endpoint(base: str) -> str:
    return base.rstrip("/") + "/chat/completions"


def extract_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    start, end = stripped.find("{"), stripped.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("External agent did not return a JSON object")
    return json.loads(stripped[start : end + 1])


def request_plan(values: dict[str, str], system_prompt: str, user_prompt: str) -> tuple[dict, dict, list[dict]]:
    failures: list[dict] = []
    for provider, model, base, key_name in PROVIDERS:
        key = values.get(key_name)
        if not key:
            failures.append({"timestamp": now(), "action": f"skip {provider}/{model}: missing configured credential", "exit_code": 1})
            continue
        body = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
        }).encode()
        request = urllib.request.Request(
            endpoint(base), data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read()
            payload = json.loads(raw)
            content = payload["choices"][0]["message"]["content"]
            plan = extract_json(content)
            identity = {"provider": provider, "model_id": payload.get("model", model), "version_or_date": now()[:10], "reasoning_setting": "temperature=0"}
            trace = {"timestamp": now(), "action": f"request sealed replay plan from {provider}/{model}", "exit_code": 0, "input_sha256": sha_bytes(body), "output_sha256": sha_bytes(raw)}
            return plan, identity, [trace, *failures]
        except (OSError, KeyError, ValueError, json.JSONDecodeError, urllib.error.HTTPError) as exc:
            failures.append({"timestamp": now(), "action": f"{provider}/{model} failed: {type(exc).__name__}", "exit_code": 1})
    raise RuntimeError("No configured external replay provider returned a valid plan")


def copy_sealed(sealed: Path, work: Path) -> None:
    expected = {"task.json", "runner.py", "agent_task.txt", "manifest.json"}
    actual = {path.name for path in sealed.iterdir() if path.is_file()}
    if actual != expected:
        raise RuntimeError(f"Unexpected sealed bundle files: {sorted(actual ^ expected)}")
    work.mkdir(parents=True, exist_ok=False)
    for name in sorted(expected):
        shutil.copy2(sealed / name, work / name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--replay-python", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    wp4b = json.loads((project / "data/science_v0.3/decisions/wp4b/gate_v2_4p_decision.json").read_text(encoding="utf-8"))
    if wp4b.get("status") != "PASSED":
        raise RuntimeError("Gate V2-4P is not PASSED; WP5 execution is forbidden")
    if not args.replay_python.is_file():
        raise RuntimeError("The isolated replay Python executable is unavailable")
    unshare = shutil.which("unshare")
    if unshare is None:
        raise RuntimeError("unshare is required for project-tree and network isolation")

    preparer = project / "scripts/science_v0.3/prepare_wp5_sealed_bundle.py"
    subprocess.run([os.sys.executable, str(preparer), "--project", str(project)], check=True)
    replay_root = project / "runs/science_v0.3/wp5_external_replay"
    sealed = replay_root / "sealed_input"
    run_id = "wp5-external-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    host_work = Path("/tmp") / run_id
    copy_sealed(sealed, host_work)

    task_prompt = (sealed / "agent_task.txt").read_text(encoding="utf-8")
    manifest_text = (sealed / "manifest.json").read_text(encoding="utf-8")
    system_prompt = "Act only as an independent scientific replay planner. Return strict JSON and never invent target values or commands."
    user_prompt = task_prompt + "\nSealed manifest:\n" + manifest_text
    values = parse_env(project / ".env")
    plan, model, tool_calls = request_plan(values, system_prompt, user_prompt)
    required_plan = {"action": "RUN_REGISTERED_REPLAY", "runner": "runner.py", "output": "result.json"}
    if any(plan.get(key) != value for key, value in required_plan.items()):
        raise RuntimeError(f"External plan violates allowlist: {plan}")
    plan_bytes = (json.dumps(plan, ensure_ascii=False, sort_keys=True) + "\n").encode()
    (host_work / "external_agent_plan.json").write_bytes(plan_bytes)

    replay_python = str(args.replay_python)
    namespace_script = (
        'mount --make-rprivate / && mount -t tmpfs tmpfs /mnt && '
        'cd "$1" && exec "$2" runner.py'
    )
    command = [
        unshare, "--user", "--map-root-user", "--mount", "--net",
        "bash", "-c", namespace_script, "wp5-replay", str(host_work), replay_python,
    ]
    blocked_env = {"OPENAI_API_KEY", "PYTHONPATH", "PYTHONHOME", "CONDA_PREFIX", "CONDA_DEFAULT_ENV", "MAMBA_ROOT_PREFIX"}
    run_env = {
        key: value for key, value in os.environ.items()
        if not key.endswith("_API_KEY") and key not in blocked_env
    }
    run_env.update({"OMP_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    started = now()
    completed = subprocess.run(command, text=True, capture_output=True, env=run_env, check=False)
    command_event = {
        "timestamp": started,
        "action": "execute allowlisted runner in unshare network/mount namespace with the project mount hidden",
        "working_directory": str(host_work),
        "exit_code": completed.returncode,
        "input_sha256": sha(host_work / "task.json"),
        "output_sha256": sha_bytes(completed.stdout.encode() + completed.stderr.encode()),
    }
    result_path = host_work / "result.json"
    if completed.returncode != 0 or not result_path.exists():
        raise RuntimeError(f"Sealed quantum replay failed with exit code {completed.returncode}")
    frozen_result_sha = sha(result_path)

    # Unblind only after the replay result has been hashed.
    contract = json.loads((project / "configs/science_v0.3/wp5_external_replay_contract.json").read_text(encoding="utf-8"))
    reference = json.loads((project / contract["target"]["reference_record"]).read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    reference_energy = float(reference["programs"]["PySCF"]["energy_hartree"])
    difference = abs(float(result["energy_hartree"]) - reference_energy)
    comparison_pass = bool(result["converged"]) and difference <= float(contract["target"]["comparison_tolerance_hartree"])

    retained = replay_root / "retained" / run_id
    retained.mkdir(parents=True, exist_ok=False)
    for path in host_work.iterdir():
        if path.is_file():
            shutil.copy2(path, retained / path.name)
    environment_lock = project / "locks/science_v0.3/ai4orgchem-v03-replay.explicit.txt"
    sensitive_pattern = re.compile(r"(?:sk-[A-Za-z0-9_-]{12,}|(?:API_KEY|TOKEN|SECRET)\s*[=:]\s*\S+)", re.I)
    findings = []
    for path in retained.iterdir():
        if path.suffix in {".json", ".txt", ".py", ".log"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if sensitive_pattern.search(text):
                findings.append(path.name)
    redaction_pass = not findings
    replay_pass = comparison_pass and redaction_pass
    bundle = {
        "schema_version": "1.0",
        "run_id": run_id,
        "model": model,
        "prompt_record": {
            "system_prompt_sha256": sha_bytes(system_prompt.encode()),
            "task_prompt_sha256": sha_bytes(user_prompt.encode()),
            "public_summary": "External model inspected a sealed no-target-value manifest and selected the only registered replay action.",
            "sensitive_text_stored": False,
        },
        "tool_calls": tool_calls,
        "commands": [command_event],
        "patches": [],
        "human_interventions": [{"timestamp": now(), "action": "User authorized sequential WP4-B, WP5 and WP6 execution", "exit_code": None}],
        "failures_and_retries": [row for row in tool_calls if row["exit_code"] != 0],
        "evidence_graph": [
            {"path": str((retained / "manifest.json").relative_to(project)).replace("\\", "/"), "sha256": sha(retained / "manifest.json"), "role": "sealed_input_manifest"},
            {"path": str((retained / "external_agent_plan.json").relative_to(project)).replace("\\", "/"), "sha256": sha(retained / "external_agent_plan.json"), "role": "external_agent_plan"},
            {"path": str((retained / "result.json").relative_to(project)).replace("\\", "/"), "sha256": frozen_result_sha, "role": "pre_unblind_quantum_result"},
        ],
        "environment": {"lock_path": str(environment_lock.relative_to(project)).replace("\\", "/"), "lock_sha256": sha(environment_lock)},
        "redaction_scan": {"status": "PASS" if redaction_pass else "FAIL", "scanner": "wp5-local-pattern-scan-v1", "findings": findings},
    }
    bundle_path = retained / "agent_run_bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    decision = {
        "schema_version": "science-v0.3-gate-v2-5-decision-1",
        "status": "PASSED" if replay_pass else "NOT_PASSED",
        "replay_status": "EXTERNAL_CLEAN_REPLAY" if replay_pass else "NOT_REPLAYED",
        "agent_maturity": "M2" if replay_pass else "M1_PLUS",
        "external_replayer": True,
        "external_model": model,
        "bundle_only_filesystem": True,
        "network_unshared_during_quantum_calculation": True,
        "scientific_grade_modified": False,
        "result_sha256_frozen_before_unblinding": frozen_result_sha,
        "reference_energy_hartree": reference_energy,
        "replay_energy_hartree": float(result["energy_hartree"]),
        "absolute_difference_hartree": difference,
        "tolerance_hartree": float(contract["target"]["comparison_tolerance_hartree"]),
        "comparison_pass": comparison_pass,
        "redaction_pass": redaction_pass,
        "run_bundle": str(bundle_path.relative_to(project)).replace("\\", "/"),
    }
    decision_path = project / "data/science_v0.3/decisions/wp5/gate_v2_5_decision.json"
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if replay_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
