from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


PRIVATE = (
    re.compile(r"D:\\AI4Science\\AI4OrgChem", re.I),
    re.compile(r"${PROJECT_ROOT}", re.I),
    re.compile(r"/home/(?:cascade|chenxiao)", re.I),
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{12,}|(?:API_KEY|TOKEN|SECRET)\s*[=:]\s*[^\s\"']+)",
    re.I,
)
FORBIDDEN_NAMES = {".env", "SC-016-D4SC08225G-s001.pdf", "SC-016-D4SC08225G-s002.zip"}


def sanitized(text: str) -> str:
    text = text.replace("\r\n", "\n")
    for pattern in PRIVATE:
        text = pattern.sub("${PROJECT_ROOT}", text)
    return text


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    status = json.loads((project / "configs/science_v0.3/v0.3_release_status.json").read_text(encoding="utf-8"))
    allowed_status = status.get("status") == "RELEASE_PACKAGE_AUTHORIZED_NOT_YET_BUILT" or (
        args.refresh and status.get("status") == "RELEASE_PACKAGE_READY"
    )
    if not allowed_status:
        raise RuntimeError("WP6 release status is not authorized")
    target = (project / "github-release/AI4OrgChem/science-v0.3").resolve()
    expected = (project / "github-release/AI4OrgChem/science-v0.3").resolve()
    if target != expected or project not in target.parents:
        raise RuntimeError(f"Unsafe release target: {target}")
    if target.exists():
        if not args.refresh:
            raise RuntimeError("V0.3 staging exists; use --refresh")
        shutil.rmtree(target)
    target.mkdir(parents=True)

    exact = [
        "configs/science_v0.3/v0.3_release_status.json",
        "configs/science_v0.3/wp2_open_three_program_contract.json",
        "configs/science_v0.3/wp4a_source_aligned_contract.json",
        "configs/science_v0.3/wp4b_paired_pilot_contract.json",
        "configs/science_v0.3/wp4b_source_0k_anchors.json",
        "configs/science_v0.3/wp5_external_replay_contract.json",
        "configs/science_v0.3/wp6_release_contract.json",
        "configs/science_v0.2/agent_run_bundle.schema.json",
        "data/processed/p12_annulene_boundary_v0.1.json",
        "data/science_v0.2/decisions/wp1/gate_v2_1_decision.json",
        "data/science_v0.2/decisions/wp3/gate_v2_3_decision.json",
        "data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json",
        "data/science_v0.3/decisions/wp4a/gate_v2_4a_decision.json",
        "data/science_v0.3/decisions/wp4b/gate_v2_4p_decision.json",
        "data/science_v0.3/decisions/wp5/gate_v2_5_decision.json",
        "data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json",
        "data/science_v0.3/processed/wp4b/wp4b_paired_pilot_summary.json",
        "data/science_v0.3/inputs/wp4b/input_manifest.json",
        "locks/science_v0.3/ai4orgchem-v02-wp2.environment.yml",
        "locks/science_v0.3/ai4orgchem-v02-wp2.explicit.txt",
        "locks/science_v0.3/ai4orgchem-v03-replay.explicit.txt",
        "docs/project/AI4OrgChem_V0.3科学闭合执行表.md",
        "tests/science_v0.3/test_wp2_open_lane.py",
    ]
    globs = [
        "data/science_v0.3/raw/wp2/anchors/*.json",
        "data/science_v0.3/raw/wp4b/*.json",
        "data/science_v0.3/inputs/wp4b/*.xyz",
        "docs/releases/science_v0.3/**/*.md",
        "scripts/science_v0.3/*.py",
    ]
    sources = {project / value for value in exact}
    for pattern in globs:
        sources.update(path for path in project.glob(pattern) if path.is_file())
    wp5 = json.loads((project / "data/science_v0.3/decisions/wp5/gate_v2_5_decision.json").read_text(encoding="utf-8"))
    bundle = project / wp5["run_bundle"]
    sources.add(bundle)
    for artifact in json.loads(bundle.read_text(encoding="utf-8"))["evidence_graph"]:
        sources.add(project / artifact["path"])

    for source in sorted(sources):
        if not source.is_file():
            raise FileNotFoundError(source)
        if source.name in FORBIDDEN_NAMES or source.suffix.lower() in {".zip", ".pdf"}:
            raise RuntimeError(f"Forbidden release input: {source}")
        relative = source.relative_to(project)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = sanitized(source.read_text(encoding="utf-8", errors="strict"))
        if CREDENTIAL_ASSIGNMENT.search(text):
            raise RuntimeError(f"Secret-like content in {relative}")
        destination.write_text(text, encoding="utf-8", newline="\n")

    readme = """# AI4OrgChem Science V0.3 / 科学闭合版

V0.3 adds the seven strictly ordered scientific-closure results without modifying V0.1 or V0.2. It contains frozen contracts, machine decisions, selected machine-readable evidence, reconstruction/validation scripts, and the redacted external replay record. It does not redistribute the monograph or third-party supplement archives.

V0.3 在不改写 V0.1、V0.2 的前提下发布七项严格顺序科学闭合结果，包含冻结合同、机器判定、精选机器证据、重建/验证脚本和脱敏外部重放记录；不再分发原著或第三方补充材料归档。

Scientific scope: V0.3 does not rewrite P01-P14, does not merge the source-aligned CESE and physical-state ASE estimands, and does not claim a universal annulene-size law, industrial ML generalization, peer review, or institutional/model-provider certification.

科学边界：V0.3不改写P01-P14，不合并source-aligned CESE与physical-state ASE两个估计量，也不宣称普遍轮烯尺寸定律、工业级机器学习泛化、同行评审结论或机构/模型厂商认证。

See `docs/releases/science_v0.3/V0.3_RELEASE_NOTES.md`, `docs/releases/science_v0.3/reports/V0.3_PRE_RELEASE_REVIEW.md`, `configs/science_v0.3/v0.3_release_status.json`, and `sha256-manifest.json` for the release scope, review state, machine decisions, and file hashes.

## Fast verification / 快速验证

Run from this `science-v0.3` directory with Python 3.11+ and `pytest`, `PyYAML`, and `jsonschema` available:

```bash
python scripts/science_v0.3/validate_github_v03_release.py --project . --package .
python scripts/science_v0.3/validate_wp4a_source_aligned.py
python scripts/science_v0.3/validate_wp4b_paired_pilot.py --project .
python scripts/science_v0.3/validate_wp5_external_replay.py --project .
python -m pytest -p no:cacheprovider tests/science_v0.3
```

These commands validate published records, hashes, estimand boundaries, replay provenance, and scope statements. They do not launch expensive quantum-chemistry calculations. Full scientific reruns require the separately documented locked environments and computational resources.

以上命令验证公开记录、哈希、估计量边界、重放来源和范围声明，不会启动昂贵量子化学计算。完整科学重算仍需使用单独记录的锁定环境和计算资源。
"""
    (target / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    rows = []
    for path in sorted(target.rglob("*")):
        if path.is_file() and path.name != "sha256-manifest.json":
            rows.append({"path": path.relative_to(target).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    manifest = {"schema_version": "science-v0.3-release-manifest-1", "version": "0.3.0", "files": rows}
    (target / "sha256-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "target": str(target), "files": len(rows) + 1}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
