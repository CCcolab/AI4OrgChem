# AI4OrgChem Science `v0.3.0` / 科学闭合版

`v0.3.0` adds the seven strictly ordered scientific-closure results without modifying `v0.1.x` or `v0.2.0`. It contains frozen contracts, machine decisions, selected machine-readable evidence, reconstruction/validation scripts, and the redacted external replay record. It does not redistribute the monograph or third-party supplement archives.

`v0.3.0`在不改写`v0.1.x`、`v0.2.0`的前提下发布七项严格顺序科学闭合结果，包含冻结合同、机器判定、精选机器证据、重建/验证脚本和脱敏外部重放记录；不再分发原著或第三方补充材料归档。

Scientific scope: `v0.3.0` does not rewrite P01-P14, does not merge the source-aligned CESE and physical-state ASE estimands, and does not claim a universal annulene-size law, industrial ML generalization, peer review, or institutional/model-provider certification.

科学边界：`v0.3.0`不改写P01-P14，不合并source-aligned CESE与physical-state ASE两个估计量，也不宣称普遍轮烯尺寸定律、工业级机器学习泛化、同行评审结论或机构/模型厂商认证。

See `docs/releases/science_v0.3/V0.3_RELEASE_NOTES.md`, `docs/releases/science_v0.3/reports/V0.3_PRE_RELEASE_REVIEW.md`, `docs/releases/science_v0.3/reports/V0.3_PUBLICATION_COMPLETION.md`, `configs/science_v0.3/v0.3_release_status.json`, and `sha256-manifest.json` for the release scope, pre-release review, publication completion, machine decisions, and file hashes.

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
