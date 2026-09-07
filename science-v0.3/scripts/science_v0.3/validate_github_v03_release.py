from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{12,}|(?:API_KEY|TOKEN|SECRET)\s*[=:]\s*[^\s\"']+)",
    re.I,
)
PRIVATE = re.compile(r"(?:D:\\AI4Science\\AI4OrgChem|${PROJECT_ROOT}|/home/(?:cascade|chenxiao))", re.I)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--package",
        type=Path,
        help="Validate an already assembled science-v0.3 package directly.",
    )
    args = parser.parse_args()
    target = (
        args.package.resolve()
        if args.package is not None
        else args.project.resolve() / "github-release/AI4OrgChem/science-v0.3"
    )
    manifest_path = target / "sha256-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    listed = {row["path"]: row for row in manifest["files"]}
    actual = {
        path.relative_to(target).as_posix(): path
        for path in target.rglob("*")
        if path.is_file() and path.name != "sha256-manifest.json"
    }
    assert set(listed) == set(actual)
    for relative, path in actual.items():
        assert sha(path) == listed[relative]["sha256"]
        assert path.stat().st_size == listed[relative]["bytes"]
        assert path.name not in {".env", "SC-016-D4SC08225G-s001.pdf", "SC-016-D4SC08225G-s002.zip"}
        assert path.suffix.lower() not in {".zip", ".pdf", ".exe", ".dll", ".so"}
        text = path.read_text(encoding="utf-8")
        assert not CREDENTIAL_ASSIGNMENT.search(text), relative
        assert not PRIVATE.search(text), relative
    status = json.loads((target / "configs/science_v0.3/v0.3_release_status.json").read_text(encoding="utf-8"))
    assert status["version"] == "0.3.0"
    assert status["status"] in {
        "RELEASE_PACKAGE_AUTHORIZED_NOT_YET_BUILT",
        "RELEASE_PACKAGE_READY",
        "COMPLETED_AND_POST_TAG_VERIFIED",
    }
    assert status["v0_1_v0_2_mutated"] is False
    assert status.get("local_package_review") in {
        "AUTHORIZED_NOT_YET_BUILT",
        "PASSED",
    }
    if status.get("local_package_review") == "PASSED":
        assert status.get("staged_file_count") == len(actual) + 1
    if status["status"] == "COMPLETED_AND_POST_TAG_VERIFIED":
        assert status.get("remote_tag_created") is True
        assert status.get("github_release_created") is True
        assert status.get("post_tag_clean_clone_verified") is True
        publication = status.get("publication", {})
        assert publication.get("tag") == "v0.3.0"
        assert publication.get("tag_commit") == "6f0370e210c6479f947c4a8fe92e8043e1d750e0"
        assert publication.get("public_download_verified") is True
    else:
        assert status.get("remote_tag_created") is False
        assert status.get("github_release_created") is False
        assert status.get("post_tag_clean_clone_verified") is False
    required = (
        "docs/releases/science_v0.3/V0.3_RELEASE_NOTES.md",
        "docs/releases/science_v0.3/reports/V0.3_PRE_RELEASE_REVIEW.md",
        "docs/releases/science_v0.3/reports/WP2_GATE_V2_2_OPEN_THREE_PROGRAM_REPORT.md",
        "docs/releases/science_v0.3/reports/WP4B_GATE_V2_4P_REPORT.md",
        "locks/science_v0.3/ai4orgchem-v02-wp2.environment.yml",
        "locks/science_v0.3/ai4orgchem-v02-wp2.explicit.txt",
        "tests/science_v0.3/test_wp2_open_lane.py",
    )
    assert all(relative in actual for relative in required)
    wp4b_report = (target / "docs/releases/science_v0.3/reports/WP4B_GATE_V2_4P_REPORT.md").read_text(encoding="utf-8")
    assert "-2.028449" in wp4b_report
    assert "因此停止规则尚未满足" not in wp4b_report
    notes = (target / required[0]).read_text(encoding="utf-8")
    assert "does not alter the P01-P14 classification matrix" in notes
    assert (
        "Remote publication identifiers are intentionally pending" in notes
        or "COMPLETED_AND_POST_TAG_VERIFIED" in notes
    )
    print("WP6_V03_RELEASE_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
