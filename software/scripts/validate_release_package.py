from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifests" / "sha256-manifest.json"
INVENTORY = ROOT / "manifests" / "FILE_INVENTORY.md"

FORBIDDEN_NAMES = {
    ".env",
    "RELEASE_STATUS.json",
    "PUBLISH_POLICY.md",
    "publish-allowlist-v0.1.yaml",
    "publication-validation.json",
}
FORBIDDEN_SUFFIXES = {
    ".pdf",
    ".epub",
    ".mobi",
    ".chk",
    ".gbw",
    ".wfn",
    ".wfx",
    ".cube",
    ".molden",
    ".pyc",
    ".pt",
    ".pth",
    ".ckpt",
}
FORBIDDEN_DIRECTORIES = {
    "publication",
    "WSL2",
    "runs",
    "artifacts",
    "tmp",
    "outputs",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
}
IGNORED_DIRECTORIES = {".git"}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".cff",
    ".toml",
    ".sh",
    "",
}
SECRET = re.compile(
    r"sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]{16,}|"
    r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"
)
LOCAL_PATH = re.compile(
    r"[A-Za-z]:\\(?:Users|AI4Science)\\|/home/[A-Za-z0-9._-]+|localhost:\d+"
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
INVENTORY_ROW = re.compile(r"^\| `([^`]+)` \|", re.MULTILINE)
MAX_FILE_BYTES = 25 * 1024 * 1024


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_DIRECTORIES for part in path.relative_to(ROOT).parts)
    )


def validate_markdown_links(path: Path, text: str, failures: list[str]) -> None:
    relative = path.relative_to(ROOT).as_posix()
    for raw_target in MARKDOWN_LINK.findall(text):
        target = unquote(raw_target.strip().strip("<>").split("#", 1)[0])
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().exists():
            failures.append(f"broken Markdown link: {relative} -> {target}")


def validate_text_file(path: Path, failures: list[str]) -> None:
    relative = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    if SECRET.search(text):
        failures.append(f"secret-like content: {relative}")
    if LOCAL_PATH.search(text):
        failures.append(f"local path or localhost content: {relative}")
    if b"\r\n" in path.read_bytes():
        failures.append(f"CRLF text would change across Git platforms: {relative}")

    suffix = path.suffix.lower()
    try:
        if suffix == ".md":
            validate_markdown_links(path, text, failures)
        elif suffix == ".py":
            ast.parse(text, filename=relative)
        elif suffix == ".json":
            json.loads(text)
        elif suffix == ".jsonl":
            for number, line in enumerate(text.splitlines(), start=1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        failures.append(f"JSONL syntax error: {relative}:{number}")
        elif suffix in {".yaml", ".yml", ".cff"}:
            parsed = yaml.safe_load(text)
            if suffix == ".cff":
                required = {"cff-version", "message", "title", "type", "authors"}
                if not isinstance(parsed, dict) or not required.issubset(parsed):
                    failures.append(f"CFF required fields missing: {relative}")
                elif not isinstance(parsed.get("authors"), list) or not parsed["authors"]:
                    failures.append(f"CFF authors missing: {relative}")
                elif any(
                    not isinstance(author, dict)
                    or not {"given-names", "family-names"}.issubset(author)
                    for author in parsed["authors"]
                ):
                    failures.append(f"CFF author name fields incomplete: {relative}")
    except (SyntaxError, json.JSONDecodeError, yaml.YAMLError) as exc:
        failures.append(f"syntax error: {relative}: {exc}")


def validate_workflow(failures: list[str]) -> None:
    workflow = ROOT / ".github" / "workflows" / "validate.yml"
    if not workflow.is_file():
        failures.append("missing GitHub Actions workflow")
        return
    text = workflow.read_text(encoding="utf-8")
    required = (
        "permissions:\n  contents: read",
        "validate_release_package.py",
        "validate_public_evidence.py",
        "validate_evidence_navigation.py",
        "validate_wsl_release.py",
        "pytest",
    )
    for token in required:
        if token not in text:
            failures.append(f"GitHub workflow missing required gate: {token}")
    for token in ("secrets.", "OPENAI_API_KEY", "curl ", "wget ", "sudo "):
        if token in text:
            failures.append(f"GitHub workflow contains forbidden operation: {token}")


def main() -> int:
    failures: list[str] = []
    manifest_rows = 0
    files = repository_files()
    by_hash: dict[str, list[str]] = defaultdict(list)

    for path in files:
        relative_path = path.relative_to(ROOT)
        relative = relative_path.as_posix()
        by_hash[digest(path)].append(relative)
        if path.name in FORBIDDEN_NAMES or path.name.startswith(".env."):
            failures.append(f"forbidden file: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden suffix: {relative}")
        if any(part in FORBIDDEN_DIRECTORIES for part in relative_path.parts):
            failures.append(f"forbidden directory component: {relative}")
        if path.stat().st_size == 0:
            failures.append(f"zero-byte file: {relative}")
        if path.stat().st_size > MAX_FILE_BYTES:
            failures.append(f"file exceeds 25 MiB: {relative}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            validate_text_file(path, failures)

    for paths in by_hash.values():
        if len(paths) > 1:
            failures.append(f"exact duplicate files: {', '.join(paths)}")

    if not MANIFEST.is_file():
        failures.append("SHA-256 manifest missing")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        rows = {row["path"]: row for row in manifest.get("files", [])}
        manifest_rows = len(rows)
        actual = {
            path.relative_to(ROOT).as_posix(): path for path in files if path != MANIFEST
        }
        if set(rows) != set(actual):
            failures.append("manifest file set differs from repository files")
        for relative, path in actual.items():
            if rows.get(relative, {}).get("sha256") != digest(path):
                failures.append(f"manifest digest mismatch: {relative}")

    if not INVENTORY.is_file():
        failures.append("file inventory missing")
    else:
        listed = set(INVENTORY_ROW.findall(INVENTORY.read_text(encoding="utf-8")))
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in files
            if "manifests" not in path.relative_to(ROOT).parts
        }
        if listed != expected:
            failures.append("file inventory set differs from substantive repository files")

    validate_workflow(failures)
    result = {
        "status": "PASS" if not failures else "FAIL",
        "repository_files": len(files),
        "manifest_rows": manifest_rows,
        "duplicate_groups": sum(1 for paths in by_hash.values() if len(paths) > 1),
        "workflow_uses_secrets": False,
        "expensive_quantum_chemistry_in_ci": False,
        "failure_count": len(failures),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
