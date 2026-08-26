> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P12 annulene size-boundary data card v0.1

## Scope

Six source-native published numeric records: `[12]`, `[14]`, `[16]`, `[18]`,
`[20]`, and `[22]annulene`. Values are transcribed from Chapter 9, Tables 9-5
and 9-8 of *Questioning Fundamental Principles of Organic Chemistry* and are
recomputed under protocol `p12-annulene-size-boundary/0.1`.

## Fields

- `VDE`, `ESE`, `CESE`, `delta_EA`, adjacent and nonadjacent local increments;
- per-pi-electron normalization;
- printed-precision identity residuals;
- `|CESE|/|sum of local increments|`;
- 4n or 4n+2 series and before/onset/after boundary role.

## Independent comparison

Van Nyvel, Alonso and Sola, *Chemical Science* 2025, 16, 5613-5622,
DOI `10.1039/D4SC08225G`. Only the neutral energetic size trend is compared.
Its ASE/ISE-II quantity is not relabeled as CESE.

## Fitness and limitations

Suitable for checking the arithmetic and interpretation of the monograph's
published P12 size-boundary argument. It is not a quantum-chemistry trajectory,
historical program reproduction, production label dataset, MACE training set,
or proof that the exact N=16/N=18 onset is estimator-independent.

Final classification: **partially consistent**. The qualitative large-ring
limit is consistent with the monograph; the exact onset is inconsistent across
the source CESE and independent ASE estimators (`N=16/18` versus `N>30`).
