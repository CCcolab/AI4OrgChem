> **Current-evidence note (2026-09-08):** P11-B was recalculated with the author's 2007 state-specific restricted-optimization method. The earlier fixed-geometry proxy is preserved as a superseded diagnostic, not used for the current classification.

# P11-B 氰基苯取代基效应数据卡 v0.2

## 范围与方法

- 体系：cyanobenzene `C7H5N`及benzene `C6H6`；
- 状态：氰基苯10态、苯3态，共13态；
- 方法：B3LYP/6-31G(d)，source-2007 Fock/overlap条件SCF，不删除ERI，不额外屏蔽hcore；
- 几何：每一状态独立优化，所有原子`z=0`硬约束；
- 原著程序代码：未使用。

## 输出

- `ESE(SB)=-37.352830 kcal/mol`（原著约`-37.3`）；
- `ESE(Ph)=-38.525952 kcal/mol`（原著约`-38.5`）；
- `ESE(benzene)=-39.016031 kcal/mol`（原著约`-39.0`）；
- `CE=+1.173122 kcal/mol`（原著约`+1.2`）；
- `IE=+0.490079 kcal/mol`（原著约`+0.49`）。

## 质量与判定

- 13/13状态通过优化与SCF门禁；
- 最大面外偏差`5.666e-17 Å`；
- 科学判定：`P11B_SOURCE2007_PLANAR_RECALCULATION_CONSISTENT`；
- 分类：在单一氰基苯、source-2007全平面逐态受限优化范围内与原著一致。

预设的起始环键漂移`0.001 Å`诊断未满足，观察最大值`0.002328 Å`来自氰基苯G态；该偏差公开保留且未通过放宽阈值隐藏。旧固定几何代理的`IE=-0.335714 kcal/mol`保留为历史诊断，并由本结果取代用于source-2007 P11-B定判。

本数据不得作为普遍取代基定律、生产标签或AI训练标签。
