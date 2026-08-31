> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P06 Target B Table 5-19范围化科学结论

- 日期：2026-08-20
- 命题：P06 非键σ–σ条件态能量差应独立分析
- 判定：**P06_SCOPED_NONBONDED_SIGMA_SIGMA_DESTABILIZATION_SUPPORTED_AT_BOTH_POINTS**
- 范围：parent N-benzylideneaniline source-geometry candidate，0°/17°，RHF/STO-3G
- 证据身份：**同一分子的两个source-proxy端点，不是跨分子或连续角度序列**

| 角度 | E_FUL (Eh) | E_PDSI (Eh) | E_PDSI-E_FUL (Eh) | kcal/mol | Table 5-19 (Eh) | 误差 (Eh) | 标签 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.0 | -546.083125240065 | -546.015168136356 | +0.067957103709 | +42.643726 | +0.06891 | 0.000952896291 | `nonbonded_sigma_sigma_source_endpoint_destabilizing_at_both_table_5_19_source_proxy_points` |
| 17.0 | -546.083106162735 | -546.020352538447 | +0.062753624288 | +39.378494 | +0.06504 | 0.002286375712 | `nonbonded_sigma_sigma_source_endpoint_destabilizing_at_both_table_5_19_source_proxy_points` |

## 结论

在FUL到PDSI只释放bonded-σ A/P隔离的source定义下，同一分子0°和17°的 `E_PDSI-E_FUL` 均为正。因此，两个冻结Table 5-19 source-proxy端点中的非键σ–σ条件态效应均表现为去稳定化。17°端点比0°低 `0.005203479422 Eh`（`3.265233 kcal/mol`），说明在这两个采样端点之间正端点幅度减小；不据此推断完整扭转曲线。

## 边界

- 这是原著FUL-2/PDSI非变分源定义的范围化端点，不是普通RHF变分相互作用能。
- 不能直接等同为所有体系的经典位阻排斥能。
- 不与Target A/C的不同方法、基组和状态能量直接相加。
- 不生成生产ML标签，不允许MACE/PySR训练或工业级泛化。
- P07仍需在不跨协议相加的前提下完成命题级整合。
