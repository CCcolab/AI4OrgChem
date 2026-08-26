> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P05 Target A范围化π–σ判定协议 v0.1

- 日期：2026-08-20
- 命题：P05
- Target：A
- 状态：范围化科学发布协议
- 原著程序代码：未使用

## 1. 唯一观测量

在冻结的Table 5-15固定parent刚性扭转source-proxy账本中定义：

`Delta E_pi_sigma(theta) = E_G(theta) - E_FUD(theta)`。

符号阈值固定为 `1.0e-8 Eh`：

- `Delta E_pi_sigma > +1.0e-8 Eh`：source-defined π–σ净端点为去稳定化；
- `Delta E_pi_sigma < -1.0e-8 Eh`：source-defined π–σ净端点为稳定化；
- 其余：容差内不能判定。

该符号只解释原著Table 5-15非变分源定义端点，不将其等同于普通RHF变分相互作用能。

## 2. 冻结受测域

- 分子：当前diphenyl imine parent NBA source-proxy；
- 几何：同一parent的0°和17°固定刚性扭转；
- 电子结构：RHF/6-31G(d)，PySCF 2.14.0；
- 状态：G与FUD；
- 能量账本：原始RHF泛函作用于source-defined密度；
- 公式：原著5-12至5-16。

不增加分子、角度或基组，不迁移Table 5-19优化几何，也不宣称历史Cartesian坐标完全一致。

## 3. 直接作用—轨道响应恒等式

每个点必须满足：

`direct_total + orbital_response_total = E_G - E_FUD`

其中：

- `direct_total = direct_intrafragment + direct_interfragment`；
- `orbital_response_total = pi_response + sigma_response`。

闭合容差为 `1.0e-9 Eh`。直接项和响应项用于解释抵消关系，最终稳定化/去稳定化标签只由净端点决定。

## 4. 最终范围化判定

- 0°：净端点在阈值内，标记为 `indeterminate_within_tolerance`；
- 17°：正直接项被负轨道响应部分抵消，但净端点仍为正，标记为 `pi_sigma_source_endpoint_destabilizing_at_17deg_table_5_15_source_proxy`。

因此P05的有限命题“π–σ轨道相互作用可表现为去稳定化”在该17°受测source-proxy点获得支持。

## 5. 禁止外推

本协议不授权：

- 所有角度、所有NBA或所有分子的π–σ普遍去稳定化定律；
- 将source直接项解释为唯一物理相互作用能；
- 生产ML标签、MACE/PySR训练或工业级泛化；
- 对P06 σ–σ命题或P07综合扭曲机理提前作结论。

