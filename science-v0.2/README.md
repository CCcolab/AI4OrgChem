# AI4OrgChem Science V0.2 / 科学增强版

This self-contained evidence package strengthens the frozen V0.1 proposition matrix without rewriting it. V0.2 adds two completed scientific enhancement lanes, an auditable cross-program backend failure, one explicitly unresolved annulene lane, and an internal clean replay of deterministic evidence assembly.

本自包含证据包在不改写 V0.1 十四项判定的前提下增强证据等级。V0.2 新增两条已完成科学增强支路、一项可审计的跨程序后端失败、一条明确未决的轮烯支路，以及一次确定性证据组装的内部洁净重放。

## Status / 状态

| Work package | Result |
|---|---|
| WP1 / P09-B CBD multireference | `PASS_WITH_METHOD_SENSITIVITY`; `PARTIALLY_SUPPORTED / R2` |
| WP2 PySCF/Psi4/ORCA replication | Functional smoke passed; Psi4 no-DF backend contract failed and ORCA is unavailable; Gate V2-2 `NOT_PASSED` |
| WP3 / P10-B benzene mechanism | Gate V2-3 `PASS`; P10-B `SUPPORTED / R3`; P10-A remains a separate R2 ledger |
| WP4 / P12-B paired annulenes | Gate V2-4P `NOT_PASSED`; exact frozen A/B/C/D structures are incomplete, so no guessed result is published |
| WP5 Agent replay | `INTERNAL_CLEAN_REPLAY / M1_PLUS`; not external replay and not M2 |

V0.1 P01-P14 values and classifications remain immutable. An unresolved V0.2 enhancement lane is not converted into a negative result and does not change P12-A.

## Rebuild decisions / 重建判定

From this directory:

```bash
python scripts/science_v0.2/evaluate_wp1.py
python scripts/science_v0.2/evaluate_wp2.py
python scripts/science_v0.2/evaluate_wp3.py
python scripts/science_v0.2/evaluate_wp4_readiness.py
python scripts/science_v0.2/run_wp5_internal_clean_replay.py
python -m pytest tests/science_v0.2 -q -p no:cacheprovider
```

These commands rebuild decisions from published machine results; they do not rerun the expensive wavefunction calculations. Quantum Package source/binaries, licensed ORCA, raw scratch, host paths, secrets, and copyrighted monograph files are not distributed.

See [`docs/releases/science_v0.2/V0.2_RELEASE_NOTES.md`](docs/releases/science_v0.2/V0.2_RELEASE_NOTES.md).
