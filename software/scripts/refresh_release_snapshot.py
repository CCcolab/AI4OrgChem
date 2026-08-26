from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / "manifests"
INVENTORY = MANIFEST_DIR / "FILE_INVENTORY.md"
MANIFEST = MANIFEST_DIR / "sha256-manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_role(relative: str) -> str:
    top = relative.split("/", 1)[0]
    return {
        "project": "project-narrative",
        "evidence": "scientific-evidence",
        "manuscripts": "manuscript",
        "ai4s-agent": "agent-delivery",
        "software": "software-or-test",
        "reproducibility": "reproducibility",
        "configs": "public-configuration",
        "figures": "project-figure",
        ".github": "continuous-integration",
    }.get(top, "repository-root")


def repository_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(ROOT).parts
    )


def write_inventory() -> int:
    rows = []
    for path in repository_files():
        relative = path.relative_to(ROOT).as_posix()
        if "manifests" in path.relative_to(ROOT).parts:
            continue
        rows.append((relative, artifact_role(relative), path.stat().st_size, digest(path)))

    lines = [
        "# AI4OrgChem GitHub文件清单",
        "",
        "本清单记录GitHub洁净仓库中的实质内容文件。生成型SHA清单和本文件自身不反向列入表格。",
        "",
        f"- 实质内容文件：{len(rows)}",
        "- 状态：版本化发布快照；内容变更后必须重新生成并验证",
        "",
        "| 文件 | 角色 | 字节 | SHA-256 |",
        "|---|---|---:|---|",
    ]
    lines.extend(
        f"| `{relative}` | {role} | {size} | `{sha256}` |"
        for relative, role, size, sha256 in rows
    )
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(rows)


def write_manifest() -> int:
    rows = []
    for path in repository_files():
        if path == MANIFEST:
            continue
        relative = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "path": relative,
                "artifact_role": artifact_role(relative),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )
    payload = {
        "schema_version": 2,
        "release_target": "github_versioned_snapshot",
        "status": "snapshot_refreshed_validation_required",
        "files": rows,
    }
    MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return len(rows)


def main() -> int:
    required = (ROOT / "README.md", ROOT / "LICENSE", ROOT / "software")
    if not all(path.exists() for path in required):
        raise SystemExit(f"Refusing unexpected repository root: {ROOT}")
    inventory_rows = write_inventory()
    manifest_rows = write_manifest()
    print(
        json.dumps(
            {
                "status": "REFRESHED_VALIDATION_REQUIRED",
                "repository_root": str(ROOT),
                "inventory_rows": inventory_rows,
                "manifest_rows": manifest_rows,
                "next_command": "python software/scripts/validate_release_package.py",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
