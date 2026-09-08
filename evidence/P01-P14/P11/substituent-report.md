> **Current-evidence note (2026-09-08):** This report supersedes the fixed-geometry source-proxy interpretation for P11-B while preserving that earlier result in the audit history.

# P11-B 氰基苯取代基效应最终范围化结论

## 结论

按照作者2007方法，对氰基苯10个状态和苯3个状态分别实施B3LYP/6-31G(d)全平面受限几何优化后：

`P11B_SOURCE2007_PLANAR_RECALCULATION_CONSISTENT`

即共轭贡献和诱导贡献均为正，并在冻结容差内复现原著。P11-A呋喃LDE此前已一致，因此P11命题在当前受测范围内由“部分一致”更新为“一致”。

## 数值

| 量 | 本项目 (kcal/mol) | 原著约值 | 偏差 |
|---|---:|---:|---:|
| `ESE(SB)` | -37.352830 | -37.3 | -0.052830 |
| `ESE(Ph)` | -38.525952 | -38.5 | -0.025952 |
| `ESE(benzene)` | -39.016031 | -39.0 | -0.016031 |
| `CE=ESE(SB)-ESE(Ph)` | +1.173122 | +1.2 | -0.026878 |
| `IE=ESE(Ph)-ESE(benzene)` | +0.490079 | +0.49 | +0.000079 |

13/13状态收敛，最大面外偏差为`5.666e-17 Å`，确认π/σ划分所需的全平面约束贯穿全部几何优化。

## 为什么旧结果异号

旧计算把Figure 7重原子键长重构为固定完整几何，再在该几何上求条件态能量，得到`IE=-0.335714 kcal/mol`。作者指出2007方法要求每个G/GL/GE状态分别进行受限几何优化。补齐这一缺失步骤后，`ESE(Ph)`和`ESE(benzene)`的相对次序恢复为原著方向，IE为`+0.490079 kcal/mol`。因此旧异号是固定几何代理与原著估计量不一致造成的，不构成对原著结果的反驳。

## 透明性与边界

预设的source-start环键漂移阈值`0.001 Å`未满足；最大值`0.002328 Å`来自氰基苯G态。该诊断完整保留。Figure 7没有公开完整Cartesian与氢坐标，因此本项目仍不声称历史原厂坐标或程序身份逐点复现；结论只限单一氰基苯、source-2007状态定义及本次全平面受限优化协议。
