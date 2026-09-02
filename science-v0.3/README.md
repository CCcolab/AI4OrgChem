# Science V0.3 — WP2 open three-program reproducibility evidence

This directory is an **incremental evidence package**, not a replacement for the immutable [`science-v0.2`](../science-v0.2/README.md) release package.

WP2 asks whether ordinary-state Gaussian-style B3LYP energies and first derivatives at eight frozen anchors can be reproduced across independent quantum-chemistry implementations under one estimand. The open-source lane uses PySCF 2.14.0, Psi4 1.11, and NWChem 7.3.0 (revision 3272822; Conda package 7.3.1).

## Result

- Gate status: `PASSED_OPEN_THREE_PROGRAM`
- Core anchors: 8/8 passed
- Relative-energy pairs: 2/2 passed
- Maximum absolute-energy span: `1.8994825268237037e-08 Eh`
- Maximum Cartesian-gradient RMS difference: `3.7021645363443873e-07 Eh/bohr`
- Effect on frozen V0.1 P01–P14 classifications: **none**

The historical ORCA-specific lane remains `NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE`. NWChem is an independent open-source third implementation and is **not** represented as ORCA or as an ORCA-equivalent substitute.

## Evidence map

| Path | Purpose |
|---|---|
| [`configs/science_v0.3/wp2_open_three_program_contract.json`](configs/science_v0.3/wp2_open_three_program_contract.json) | Frozen estimand, grids, basis sets, backend rules, and thresholds |
| [`data/science_v0.3/raw/wp2/anchors/`](data/science_v0.3/raw/wp2/anchors/) | Eight compact machine-readable anchor records |
| [`data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json`](data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json) | Cross-program and relative-energy summary |
| [`data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json`](data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json) | Gate decision |
| [`docs/releases/science_v0.3/reports/WP2_GATE_V2_2_OPEN_THREE_PROGRAM_REPORT.md`](docs/releases/science_v0.3/reports/WP2_GATE_V2_2_OPEN_THREE_PROGRAM_REPORT.md) | Scientific report |
| [`scripts/science_v0.3/`](scripts/science_v0.3/) | Calibration, run, and deterministic summary entry points |
| [`locks/science_v0.3/`](locks/science_v0.3/) | Redacted NWChem environment locks |
| [`sha256-manifest.json`](sha256-manifest.json) | Package integrity inventory |

Large program logs, scratch files, and local run caches are intentionally excluded. The compact records retain energies, gradients where required, geometry/source hashes, program identities, and pass/fail comparisons.

## Verification

From the repository root:

```bash
python -m unittest science-v0.3/tests/science_v0.3/test_wp2_open_lane.py
```

To recompute an anchor, activate environments providing PySCF, Psi4, and the locked NWChem executable, then run from `science-v0.3/`:

```bash
cd science-v0.3
python scripts/science_v0.3/run_wp2_open_three_program_lane.py \
  --anchor WP2-P08-BUTADIENE-G-EG
python scripts/science_v0.3/summarize_wp2_open_three_program_gate.py
```

The runner deliberately reads the frozen source geometries and tangent definitions from the sibling `science-v0.2/` package. This dependency preserves historical inputs instead of duplicating or silently modifying them.

## 中文说明

本目录是WP2的**增量科学证据包**，不覆盖不可变的`science-v0.2`历史发布。其开源三程序支路在同一冻结估计量下，以PySCF、Psi4和NWChem复算八个普通态锚点；8/8锚点和2/2相对能量对全部通过。该结果提升跨程序复算证据，但不改动V0.1十四项命题判定，也不宣称NWChem等同或替代ORCA。原ORCA专用支路仍因本机没有获许可可执行文件而保持未建立。
