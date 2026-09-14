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
    ".envrc",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "RELEASE_STATUS.json",
    "PUBLISH_POLICY.md",
    "publish-allowlist-v0.1.yaml",
    "publication-validation.json",
}
FORBIDDEN_SUFFIXES = {
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".epub",
    ".mobi",
    ".zip",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
    ".tgz",
    ".p12",
    ".pfx",
    ".jks",
    ".kdbx",
    ".token",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".out",
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
    "implementation",
    "project_closure",
    "最终成果",
    "runs",
    "artifacts",
    "tmp",
    "outputs",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
}
IGNORED_DIRECTORIES = {".git"}
CURATED_REPLAY_RECORDS = {
    "science-v0.2/runs/science_v0.2/wp5_internal_clean_replay/replay_result.json",
    "science-v0.3/runs/science_v0.3/wp5_external_replay/retained/wp5-external-20260907T121810Z/agent_run_bundle.json",
    "science-v0.3/runs/science_v0.3/wp5_external_replay/retained/wp5-external-20260907T121810Z/external_agent_plan.json",
    "science-v0.3/runs/science_v0.3/wp5_external_replay/retained/wp5-external-20260907T121810Z/manifest.json",
    "science-v0.3/runs/science_v0.3/wp5_external_replay/retained/wp5-external-20260907T121810Z/result.json",
}
ALLOWED_SELF_CONTAINED_V03_DUPLICATES = {
    frozenset(
        {
            "science-v0.2/data/science_v0.2/decisions/wp1/gate_v2_1_decision.json",
            "science-v0.3/data/science_v0.2/decisions/wp1/gate_v2_1_decision.json",
        }
    ),
    frozenset(
        {
            "science-v0.2/data/science_v0.2/decisions/wp3/gate_v2_3_decision.json",
            "science-v0.3/data/science_v0.2/decisions/wp3/gate_v2_3_decision.json",
        }
    ),
    frozenset(
        {
            "development/science-v0.2/configs/agent_run_bundle.schema.json",
            "science-v0.2/configs/science_v0.2/agent_run_bundle.schema.json",
            "science-v0.3/configs/science_v0.2/agent_run_bundle.schema.json",
        }
    ),
}
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
    ".txt",
    ".xyz",
    "",
}
SECRET = re.compile(
    r"sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,}|Bearer\s+[A-Za-z0-9._-]{16,}|"
    r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|"
    r"(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][^\"']{12,}[\"']",
    re.IGNORECASE,
)
LOCAL_PATH = re.compile(
    r"[A-Za-z]:\\(?:Users|AI4Science)\\|/home/[A-Za-z0-9._-]+|localhost:\d+"
)
SIBLING_REPOSITORY_LINK = re.compile(
    r"https?://(?:www\.)?github\.com/CCcolab/"
    r"(?:AI4S-OrgChem|AI4S-AI4OrgChem)(?:[/#?]|$)",
    re.IGNORECASE,
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
INVENTORY_ROW = re.compile(r"^\| `([^`]+)` \|", re.MULTILINE)
MAX_FILE_BYTES = 25 * 1024 * 1024


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_loads(text: str) -> object:
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


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
    if SIBLING_REPOSITORY_LINK.search(text):
        failures.append(f"cross-project GitHub link: {relative}")
    if b"\r\n" in path.read_bytes():
        failures.append(f"CRLF text would change across Git platforms: {relative}")

    suffix = path.suffix.lower()
    try:
        if suffix == ".md":
            validate_markdown_links(path, text, failures)
        elif suffix == ".py":
            ast.parse(text, filename=relative)
        elif suffix == ".json":
            strict_json_loads(text)
        elif suffix == ".jsonl":
            for number, line in enumerate(text.splitlines(), start=1):
                if line.strip():
                    try:
                        strict_json_loads(line)
                    except (json.JSONDecodeError, ValueError) as exc:
                        failures.append(f"JSONL syntax error: {relative}:{number}: {exc}")
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
    except (SyntaxError, json.JSONDecodeError, ValueError, yaml.YAMLError) as exc:
        failures.append(f"syntax error: {relative}: {exc}")


def validate_workflow(failures: list[str]) -> None:
    workflow = ROOT / ".github" / "workflows" / "validate.yml"
    if not workflow.is_file():
        failures.append("missing GitHub Actions workflow")
        return
    text = workflow.read_text(encoding="utf-8")
    required = (
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "validate_release_package.py",
        "validate_public_evidence.py",
        "validate_p14_evidence.py",
        "validate_evidence_navigation.py",
        "validate_wsl_release.py",
        "pytest",
    )
    for token in required:
        if token not in text:
            failures.append(f"GitHub workflow missing required gate: {token}")
    for token in (
        "secrets.",
        "OPENAI_API_KEY",
        "curl ",
        "wget ",
        "sudo ",
        "pull_request_target",
        "workflow_run:",
        "contents: write",
        "id-token: write",
        "persist-credentials: true",
    ):
        if token in text:
            failures.append(f"GitHub workflow contains forbidden operation: {token}")

    allowed_actions = {"actions/checkout", "actions/setup-python"}
    pinned_action = re.compile(
        r"^\s*uses:\s*([^@\s]+)@([0-9a-f]{40})(?:\s+#.*)?$",
        re.MULTILINE,
    )
    uses_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("uses:")]
    pinned_lines = pinned_action.findall(text)
    if len(pinned_lines) != len(uses_lines):
        failures.append("every GitHub Action must be pinned to a full 40-character commit SHA")
    for action, _sha in pinned_lines:
        if action not in allowed_actions:
            failures.append(f"GitHub workflow uses an unapproved action: {action}")


def validate_computation_guide(failures: list[str]) -> None:
    guide = ROOT / "reproducibility" / "DETAILED_COMPUTATION_GUIDE_zh-CN.md"
    if not guide.is_file():
        failures.append("detailed computation guide missing")
        return
    text = guide.read_text(encoding="utf-8")
    required_sections = (
        "为什么本项目把WSL 2作为权威计算平台",
        "硬件与软件栈",
        "在WSL 2里完成的计算任务",
        "十四项 × WSL 2定判入口",
        "单次作业的数据流（WSL 2内）",
        "计算纪律（WSL 2同样强制）",
        "本目录内容（归档结构）",
        "在WSL 2中复现（操作摘要）",
        "刷新本快照",
        "相关文档",
    )
    for section in required_sections:
        if section not in text:
            failures.append(f"detailed computation guide missing: {section}")
    rows = re.findall(r"(?m)^\| (P\d{2}) \|", text)
    expected = {f"P{number:02d}" for number in range(1, 15)}
    if len(rows) != 14 or set(rows) != expected:
        failures.append("detailed guide WSL determination table must contain exactly P01-P14")
    if "WSL 2不是这些量子化学公式成立的数学前提" not in text:
        failures.append("detailed guide must distinguish canonical runtime from mathematical necessity")
    if "DETAILED_COMPUTATION_GUIDE_zh-CN.md" not in (ROOT / "README_zh-CN.md").read_text(encoding="utf-8"):
        failures.append("Chinese homepage lacks detailed-guide link")
    english_homepage = (ROOT / "README.md").read_text(encoding="utf-8")
    if "RUNBOOK_EN.md" not in english_homepage or "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md" not in english_homepage:
        failures.append("English homepage must link the English runbook and review guide")
    if "](reproducibility/DETAILED_COMPUTATION_GUIDE_zh-CN.md)" in english_homepage:
        failures.append("English homepage must not route readers directly to the Chinese-only detailed guide")


def validate_english_navigation(failures: list[str]) -> None:
    """Keep the public English entry points on English pages where available."""
    routes = {
        "README.md": (
            "manuscripts/P01-P14_evidence_matrix_EN.md",
            "project/README_EN.md",
            "manuscripts/README_EN.md",
            "ai4s-agent/README_EN.md",
            "ai4s-agent/CAPABILITIES_AND_RESULTS_EN.md",
            "ai4s-agent/LIMITATIONS_EN.md",
            "software/README_EN.md",
            "reproducibility/README_EN.md",
            "figures/README_EN.md",
            "manifests/README_EN.md",
        ),
        "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md": (
            "manuscripts/P01-P14_evidence_matrix_EN.md",
            "ai4s-agent/README_EN.md",
            "reproducibility/README_EN.md",
        ),
        "evidence/P01-P14/README.md": (
            "../../manuscripts/P01-P14_evidence_matrix_EN.md",
        ),
        "ai4s-agent/README_EN.md": (
            "SYSTEM_ARCHITECTURE_EN.md",
            "CAPABILITIES_AND_RESULTS_EN.md",
            "EVIDENCE_GOVERNANCE_EN.md",
            "LIMITATIONS_EN.md",
        ),
    }
    for source, targets in routes.items():
        document = (ROOT / source).read_text(encoding="utf-8")
        for target in targets:
            if f"]({target})" not in document:
                failures.append(f"English navigation route missing: {source} -> {target}")
            resolved = (ROOT / source).parent / target
            if not resolved.is_file():
                failures.append(f"English navigation target missing: {source} -> {target}")

    for source in ("README.md", "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md"):
        document = (ROOT / source).read_text(encoding="utf-8")
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", document):
            if target.endswith("_zh-CN.md") and not any(
                marker in label.lower() for marker in ("chinese", "中文")
            ):
                failures.append(f"Chinese target lacks language label: {source} -> {target}")
            if target in (
                "ai4s-agent/README.md",
                "figures/README.md",
                "manifests/FILE_INVENTORY.md",
                "manuscripts/README.md",
                "project/README.md",
                "reproducibility/README.md",
                "software/README.md",
            ):
                failures.append(f"English page routes to Chinese directory entry: {source} -> {target}")

    companion_path = ROOT / "evidence" / "P01-P14" / "EVIDENCE_COMPANION_EN.md"
    english_index = (ROOT / "evidence" / "P01-P14" / "README.md").read_text(encoding="utf-8")
    english_guide = (ROOT / "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md").read_text(encoding="utf-8")
    if not companion_path.is_file():
        failures.append("English proposition evidence companion missing")
    else:
        companion = companion_path.read_text(encoding="utf-8")
        headings = {
            re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")
            for heading in re.findall(r"(?m)^### (.+)$", companion)
        }
        anchors = re.findall(r"\]\(EVIDENCE_COMPANION_EN\.md#([a-z0-9-]+)\)", english_index)
        if len(anchors) != 45 or len(set(anchors)) != 45:
            failures.append("English evidence navigator must expose 45 distinct companion sections")
        for anchor in anchors:
            if anchor not in headings:
                failures.append(f"English evidence companion anchor missing: {anchor}")
        for proposition in ("p04", "p08", "p09", "p11-b"):
            if f"EVIDENCE_COMPANION_EN.md#{proposition}-report" not in english_guide:
                failures.append(f"English review guide lacks {proposition} English report route")
    if re.search(r"\]\(P\d{2}/(?:[a-z-]*-)?(?:data-card|protocol|report)\.md\)", english_index):
        failures.append("English evidence navigator links directly to a Chinese-only original record")


def validate_current_release_alignment(failures: list[str]) -> None:
    current_release = "v0.3.1"
    current_notes = ROOT / "project" / "release-history" / "RELEASE_NOTES_v0.3.1.md"
    if (ROOT / "RELEASE_NOTES_v0.3.1.md").exists():
        failures.append("v0.3.1 release notes must not appear in the homepage root file list")
    if (ROOT / "RELEASE_NOTES_v0.3.2.md").exists():
        failures.append("withdrawn v0.3.2 release notes must not appear in the homepage root file list")
    if not current_notes.is_file():
        failures.append("v0.3.1 release notes missing")
    elif not all(
        token in current_notes.read_text(encoding="utf-8")
        for token in ("Current formal release", "当前正式版本", "P12_CORRIGENDUM.md")
    ):
        failures.append("v0.3.1 notes lack the bilingual P12 page-note notice")
    release_facing = (
        ROOT / "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md",
        ROOT / "REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md",
        ROOT / "P12_CORRIGENDUM.md",
        current_notes,
    )
    for path in release_facing:
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            failures.append(f"release-facing file missing: {relative}")
            continue
        if current_release not in path.read_text(encoding="utf-8"):
            failures.append(f"release-facing file does not name {current_release}: {relative}")

    for path in release_facing + (ROOT / "project" / "README.md", ROOT / "manuscripts" / "P01-P14_evidence_matrix_zh-CN.md"):
        if path.is_file() and "v0.3.2" in path.read_text(encoding="utf-8"):
            failures.append(f"withdrawn version remains current-facing: {path.relative_to(ROOT).as_posix()}")

    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    if not isinstance(citation, dict) or str(citation.get("version")) != "0.3.1":
        failures.append("CITATION.cff version must match current release 0.3.1")
    if not isinstance(citation, dict) or str(citation.get("date-released")) != "2026-09-08":
        failures.append("CITATION.cff date must match v0.3.1 release date")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [0.3.1] - 2026-09-08" not in changelog or "## [0.3.2]" in changelog:
        failures.append("CHANGELOG.md must show v0.3.1 as the latest formal release")
    for homepage in (ROOT / "README.md", ROOT / "README_zh-CN.md"):
        text = homepage.read_text(encoding="utf-8")
        if "RELEASE_NOTES_v0.3.2.md" in text or "P12_CORRIGENDUM.md" in text:
            failures.append(f"homepage should remain version-neutral and proposition-neutral: {homepage.name}")


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
        curated_replay_record = relative in CURATED_REPLAY_RECORDS
        if any(part in FORBIDDEN_DIRECTORIES for part in relative_path.parts) and not curated_replay_record:
            failures.append(f"forbidden directory component: {relative}")
        if path.stat().st_size == 0:
            failures.append(f"zero-byte file: {relative}")
        if path.stat().st_size > MAX_FILE_BYTES:
            failures.append(f"file exceeds 25 MiB: {relative}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            validate_text_file(path, failures)

    allowed_historical_duplicate_groups = 0
    for paths in by_hash.values():
        if len(paths) <= 1:
            continue
        historical = [path for path in paths if path.startswith("development/science-v0.2/")]
        released = [path for path in paths if path.startswith("science-v0.2/")]
        if len(paths) == 2 and len(historical) == 1 and len(released) == 1:
            # The development tree is a frozen WP0 provenance snapshot.  An exact
            # copy may also occur in the self-contained V0.2 evidence package.
            allowed_historical_duplicate_groups += 1
            continue
        if frozenset(paths) in ALLOWED_SELF_CONTAINED_V03_DUPLICATES:
            # V0.3 is self-contained and carries only the narrowly enumerated
            # immutable V0.2 prerequisites required by its public validators.
            allowed_historical_duplicate_groups += 1
            continue
        failures.append(f"exact duplicate files: {', '.join(paths)}")

    if not MANIFEST.is_file():
        failures.append("SHA-256 manifest missing")
    else:
        manifest = strict_json_loads(MANIFEST.read_text(encoding="utf-8"))
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
    validate_computation_guide(failures)
    validate_english_navigation(failures)
    validate_current_release_alignment(failures)
    result = {
        "status": "PASS" if not failures else "FAIL",
        "repository_files": len(files),
        "manifest_rows": manifest_rows,
        "duplicate_groups": sum(1 for paths in by_hash.values() if len(paths) > 1),
        "allowed_historical_duplicate_groups": allowed_historical_duplicate_groups,
        "workflow_uses_secrets": False,
        "expensive_quantum_chemistry_in_ci": False,
        "failure_count": len(failures),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
