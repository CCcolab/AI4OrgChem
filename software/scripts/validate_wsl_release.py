from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    failures: list[str] = []
    required = {
        "environment": ROOT / "reproducibility" / "environment.yml",
        "runbook_en": ROOT / "reproducibility" / "RUNBOOK_EN.md",
        "runbook_zh": ROOT / "reproducibility" / "RUNBOOK_zh-CN.md",
        "matrix_en": ROOT / "reproducibility" / "PLATFORM_MATRIX_EN.md",
        "matrix_zh": ROOT / "reproducibility" / "PLATFORM_MATRIX_zh-CN.md",
        "wsl_readme": ROOT / "reproducibility" / "wsl" / "README.md",
        "activate": ROOT
        / "reproducibility"
        / "wsl"
        / "activate-ai4orgchem-public.sh",
        "verify": ROOT / "reproducibility" / "wsl" / "ai4orgchem-verify",
    }
    texts: dict[str, str] = {}
    for name, path in required.items():
        if not path.is_file():
            failures.append(f"missing required WSL release file: {path.relative_to(ROOT)}")
            continue
        texts[name] = path.read_text(encoding="utf-8")

    environment = texts.get("environment", "")
    if not re.search(r"(?m)^name:\s*ai4orgchem-public\s*$", environment):
        failures.append("public environment must be named ai4orgchem-public")

    shell_text = "\n".join(texts.get(key, "") for key in ("activate", "verify"))
    for required_token in (
        "BASH_SOURCE[0]",
        "AI4ORGCHEM_PUBLICATION_ROOT",
        "/opt/ai4orgchem/publication",
        "software/scripts/validate_public_evidence.py",
    ):
        if required_token not in shell_text:
            failures.append(f"WSL entry points missing portable token: {required_token}")

    forbidden_shell = (
        r"\bmicromamba\s+(?:update|install|remove)\b",
        r"\bconda\s+(?:update|install|remove)\b",
        r"\brm\s+-rf\b",
        r"--force\b",
    )
    for pattern in forbidden_shell:
        if re.search(pattern, shell_text):
            failures.append(f"WSL entry point contains mutating operation: {pattern}")

    if re.search(r"/home/[A-Za-z0-9._-]+", shell_text):
        failures.append("WSL entry point contains a fixed Linux user path")
    if re.search(r"[A-Za-z]:\\", shell_text):
        failures.append("WSL entry point contains a Windows drive path")
    if "localhost" in shell_text:
        failures.append("WSL entry point contains a local service address")

    combined_docs = "\n".join(
        texts.get(key, "")
        for key in ("runbook_en", "runbook_zh", "matrix_en", "matrix_zh", "wsl_readme")
    )
    for required_statement in (
        "WSL 2 / Ubuntu 24.04",
        "ai4orgchem-public",
        "/opt/ai4orgchem/publication",
    ):
        if required_statement not in combined_docs:
            failures.append(f"WSL documentation missing boundary: {required_statement}")
    if not all(
        token in combined_docs.lower()
        for token in ("native windows", "not certified", "existing environment")
    ):
        failures.append("English platform/non-overwrite boundaries are incomplete")
    if not all(token in combined_docs for token in ("原生Windows", "不会", "覆盖")):
        failures.append("Chinese platform/non-overwrite boundaries are incomplete")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "files_checked": len(required),
        "supported_layouts": ["github_clone", "fhs_opt_deployment"],
        "environment_mutation_allowed": False,
        "failure_count": len(failures),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
