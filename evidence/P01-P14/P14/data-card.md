> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P14应变芳香π-distortivity数据卡 v0.1

- 命题：P14 / CAT07
- 体系：原著10-12号benzotricyclobutadiene，C12H6
- 分类：`consistent` / **与原著一致**（v0.3.1资格门禁修正并完成生产优化后恢复）
- 协议：`p14-strained-aromatic-pi-distortivity/0.1`
- 原著程序代码：未使用

## 核心数值

| 证据 | 项目结果 | 原著锚点 | 残差 |
|---|---:|---:|---:|
| B3LYPG/6-31G(d)生产优化dΔr(GP) | 0.172204 Å | 0.179 Å | -0.006796 Å |
| B3LYPG/6-31G(d)生产优化端点 | 67.679719 kcal/mol | 67.08 kcal/mol | +0.599719 kcal/mol |
| B3LYPG/6-31G(d)固定几何端点 | 67.086899 kcal/mol | 67.08 kcal/mol | +0.006899 kcal/mol |
| 内存实现总能等价性 | 2.27e-13 Eh | 0 | 2.27e-13 Eh |

## 证据文件

- [`processed/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json`](processed/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json)
- [`processed/p14_C12H6_B3LYPG_6_31Gd_production_optimization_v0.1.json`](processed/p14_C12H6_B3LYPG_6_31Gd_production_optimization_v0.1.json)
- [`processed/p14_memory_controlled_eri_equivalence_v0.1.json`](processed/p14_memory_controlled_eri_equivalence_v0.1.json)
- [`processed/p14_C12H6_source_level_fixed_geometry_v0.1.json`](processed/p14_C12H6_source_level_fixed_geometry_v0.1.json)
- [`processed/p14_strained_aromatic_pi_distortivity_classification_v0.1.json`](processed/p14_strained_aromatic_pi_distortivity_classification_v0.1.json)

公开输入坐标见[`inputs/`](inputs/README.md)。计算入口位于`software/scripts/run_p14_*.py`，确定性底层重算入口为`software/scripts/classify_p14_strained_aromatic_pi_distortivity.py`。GitHub CI不自动运行高成本QM，只从以上冻结底层记录重算P14判据并核对文件哈希。

## 适用与禁用

该卡支持冻结C12H6 source-proxy协议内的P14范围化分类。v0.3.0使用的STO-3G记录只保留为技术烟测，不再进入科学定判。新增B3LYPG/6-31G(d) G/PLG五参数生产优化的最大梯度分别为`0.00146286/0.00116557 Eh/Å`，均低于`0.002 Eh/Å`，且无活动边界；SCF、78电子、能量闭合、对易子和密度幂等门禁全部通过。其结构响应和优化端点均在预注册容差内，因此P14恢复为“一致”。原著未公开完整Cartesian坐标，C–H采用1.080 Å代理；优化只覆盖平面D3h五参数子空间，未宣称完成全笛卡尔频率/更宽对称性搜索、19分子面板复现或普遍应变芳香定律。当前`production_label=false`、`training_eligible=false`。
