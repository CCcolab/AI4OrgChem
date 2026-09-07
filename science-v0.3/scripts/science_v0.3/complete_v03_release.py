from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    target = project / "github-release/AI4OrgChem/science-v0.3"
    manifest_path = target / "sha256-manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("Validated V0.3 staging package is absent")
    status_path = project / "configs/science_v0.3/v0.3_release_status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if status.get("status") not in {
        "RELEASE_PACKAGE_AUTHORIZED_NOT_YET_BUILT",
        "RELEASE_PACKAGE_READY",
    }:
        raise RuntimeError(f"Unexpected release status: {status.get('status')}")
    status["status"] = "RELEASE_PACKAGE_READY"
    status["staging_path"] = "github-release/AI4OrgChem/science-v0.3"
    status["local_package_review"] = "PASSED"
    status["staged_file_count"] = sum(1 for path in target.rglob("*") if path.is_file())
    status["remote_tag_created"] = False
    status["github_release_created"] = False
    status["post_tag_clean_clone_verified"] = False
    status_path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    staged_status = target / "configs/science_v0.3/v0.3_release_status.json"
    staged_status.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    rows = []
    for path in sorted(target.rglob("*")):
        if path.is_file() and path.name != "sha256-manifest.json":
            rows.append({"path": path.relative_to(target).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    manifest = {"schema_version": "science-v0.3-release-manifest-1", "version": "0.3.0", "files": rows}
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": status["status"], "files": len(rows) + 1}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
