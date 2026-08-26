> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P06 Target B Table 5-19范围化科学标签 v0.1

## 标识

- 数据：`data/processed/target_b_table_5_19_scoped_scientific_labels_v0.1.jsonl`
- 生成器：`scripts/generate_target_b_table_5_19_scoped_scientific_conclusion.py`
- 验证器：`scripts/validate_target_b_scoped_release.py`
- 协议：`docs/theory/p06_target_b_scoped_protocol_v0.1.md`
- 状态：最终范围化科学结论，非生产标签
- 记录：2个固定source-geometry candidate点，每点3个状态/端点值，共6条

## 科学含义

每个点记录：

1. `source_state_energy_E_FUL`；
2. `source_state_energy_E_PDSI`；
3. `source_endpoint_E_PDSI_minus_E_FUL`。

三者满足：

`source_state_energy_E_PDSI - source_state_energy_E_FUL = source_endpoint_E_PDSI_minus_E_FUL`。

0°和17°端点均为正，标签为 `nonbonded_sigma_sigma_source_endpoint_destabilizing_at_both_table_5_19_source_proxy_points`。该标签表示在冻结FUL-2/PDSI源定义中，释放bonded-σ A/P隔离使条件态能量升高。

## 允许用途

该数据用于复核P06在两个Table 5-19 source-proxy点的范围化结论、独立状态能量闭合、与原著端点的数值容差及扭转前后幅度变化。

## 禁止用途

- 不得等同为所有分子的经典位阻排斥能；
- 不得作为生产ML训练标签；
- 不得用于MACE、PySR或工业级泛化；
- 不得与Target A/C的不同方法、基组和状态能量直接相加；
- 不得宣称所有角度、所有NBA或所有σ–σ作用均满足同一符号。

每条记录均携带几何、源几何artifact、独立能量组装artifact、计算配置、状态合同、方法、基组、引擎、资源环境和公开来源的哈希或出处信息。

