> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P08 丁二烯 G-GL(2014) source-aligned独立重构

- 协议：`p08-butadiene-gl2014-independent/0.1`
- 判定：`P08_SCOPED_BUTADIENE_PROPOSITION_SUPPORTED`
- 优化器：`scipy_L_BFGS_B_two_point_finite_difference`，13 iterations / 160 unique evaluations
- 证据身份：**GL(2014) source-aligned独立代码重构；不是原厂程序身份复现或正交物理估计量验证**

## 最终数值

| 量 | 项目结果 | 原著GL(2014)比较值 | 绝对差 |
|---|---:|---:|---:|
| ΔEA = E(G)-E(GL) | +1.575676 kcal/mol | +1.5 | 0.075676 |
| r23(G) | 1.457809 Å | 1.457 | 0.000809 |
| r23(GL) | 1.454394 Å | 1.451 | 0.003394 |
| r23(G)-r23(GL) | +0.003415 Å | +0.006 | 0.002585 |

## 判定

- P08-A：`destabilizing`。正的 `E(G)-E(GL)` 表示原著定义下的离域端点为去稳定化。
- P08-B：三种丁烯参照给出稳定化、近零和去稳定化三类结果，因此选择性氢化热不是唯一符号证据。
- P08-C：`source_defined_delocalization_lengthens_central_sp2_sp2_single_bond`；同协议GL中央键短于G中央键。

## 技术检查

- `optimizer_reports_success`: `True`
- `optimizer_gradient_max_within_tolerance`: `True`
- `no_active_parameter_bound`: `True`
- `final_gl_scf_converged`: `True`
- `one_occupied_pi_per_fragment`: `True`
- `no_mixed_occupied_pi`: `True`
- `modified_metric_electron_count_closes`: `True`
- `delta_EA_positive`: `True`
- `r23_G_greater_than_r23_GL`: `True`
- `source_energy_value_within_comparison_tolerance`: `True`
- `source_r23_GL_within_comparison_tolerance`: `True`
- `p08_b_hydrogenation_reference_subtarget_complete`: `True`
- `ai_training_started`: `False`

## 结论边界

本结果在当前冻结的公开条件source-aligned协议内支持原著关于反式-1,3-丁二烯的三个范围化命题。项目未使用原著程序代码，也不宣称与原厂PC-GAMESS实现逐项同一。同一实现采用不同普通RKS初始密度的复算只证明收敛稳健性，不是第二套程序复现。旧CASCADE常规热化学结论及其他GL版本只作异估计量参考，不参与本判定。本结果不证明所有分子的普遍共轭去稳定化定律，也不是生产标签。当前公开证据含协议、机器结果和坐标诊断；洁净克隆的一键端到端复算入口属于V0.2待补强项，不影响V0.1冻结数值。
