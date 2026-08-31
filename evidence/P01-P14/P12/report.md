> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P12 轮烯尺寸边界范围化结论

- 协议：`p12-annulene-size-boundary/0.1`
- 证据1：原著Chapter 9、Table 9-5/9-8公开数值的独立算术重构。
- 证据2：Van Nyvel、Alonso与Solà，Chemical Science 2025，DOI `10.1039/D4SC08225G`。
- 未使用原著程序代码；未宣称历史量化程序或Cartesian坐标复现。

## 六点结果

| N | 系列 | 角色 | VDE | ΔEA | CESE | CESE/π | 相对CESE |
|---:|---|---|---:|---:|---:|---:|---:|
| 12 | `4n` | `before` | +10.40 | +12.79 | +2.59 | +0.22 | 0.254 |
| 14 | `4n_plus_2` | `before` | -32.90 | -6.89 | -16.28 | -1.16 | 1.736 |
| 16 | `4n` | `onset` | +10.10 | +15.16 | -0.65 | -0.04 | 0.041 |
| 18 | `4n_plus_2` | `onset` | -17.80 | +16.66 | -11.17 | -0.62 | 0.402 |
| 20 | `4n` | `after` | +13.70 | +22.11 | -1.51 | -0.07 | 0.064 |
| 22 | `4n_plus_2` | `after` | -23.40 | +17.78 | -9.40 | -0.42 | 0.346 |

## 判定

- `4n`系列：N=12的CESE为正；N=16与20的相对CESE分别降至约4%与6%，支持原著在其账本中把N≥16视为接近多烯。
- `4n+2`系列：N=14的ΔEA为负；N=18与22转为正，同时CESE仍为负，相对CESE约40%与35%，复现原著的边界逻辑。
- 六点VDE仍严格按4n/4n+2交替符号。因此，原著所谓“边界”不是VDE符号消失，而是CESE相对局域增量的权重下降以及ΔEA方向改变。
- 2025年独立ASE研究同样发现芳香/反芳香能量差随N增大而消失，但对中性体系给出的能量非芳香边界是N>30，而原著账本以N=16/18描述起始变化。两个估计量不同，不能把这些阈值视为同一可观测量下的直接一致或直接冲突。

最终判定：`P12_PARTIALLY_CONSISTENT_QUALITATIVE_BOUNDARY_CONSISTENT_EXACT_ONSET_NOT_DIRECTLY_COMPARABLE`。旧版机器字符串中的`CROSS_ESTIMATOR_INCONSISTENT`仅作为V0.1兼容字段保留，不再作为当前科学语义。

最准确表述是：**P12与原著部分一致：大环最终趋向能量非芳香/多烯行为的定性命题一致；原著CESE的N=16/18与独立ASE的N>30属于不同估计量下的起始尺寸，不能直接比较。该不可比性既不升级为完全一致，也不降为同估计量不一致。**

本结果不是生产标签，不进入AI训练，不启动P13。

## 自动检查

- `PASS` six_point_panel_complete
- `PASS` ESE_identities_close_at_printed_precision
- `PASS` CESE_identities_close_at_printed_precision
- `PASS` CESE_per_pi_closes_at_printed_precision
- `PASS` VDE_alternates_with_Huckel_series
- `PASS` four_n_before_boundary_is_destabilizing
- `PASS` four_n_onset_and_after_have_small_relative_CESE
- `PASS` four_n_plus_2_before_boundary_has_stabilizing_delta_EA
- `PASS` four_n_plus_2_onset_and_after_have_positive_delta_EA_negative_CESE
- `PASS` four_n_plus_2_onset_and_after_match_relative_CESE_band
- `PASS` independent_lane_uses_different_estimand
- `PASS` exact_onset_not_claimed_as_independently_reproduced
- `PASS` production_label_disabled
- `PASS` AI_training_disabled
