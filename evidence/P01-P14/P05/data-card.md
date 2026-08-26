> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P05 Target A Table 5-15范围化科学标签 v0.1

## 标识

- 数据：`data/processed/target_a_table_5_15_scoped_scientific_labels_v0.1.jsonl`
- 生成器：`scripts/generate_target_a_table_5_15_scoped_scientific_conclusion.py`
- 验证器：`scripts/validate_target_a_scoped_release.py`
- 协议：`docs/theory/p05_target_a_scoped_protocol_v0.1.md`
- 状态：最终范围化科学结论，非生产标签
- 记录：2个固定source-proxy几何点，每点3个分量，共6条

## 科学含义

每个点记录：

1. `pi_sigma_source_direct_total`；
2. `orbital_response_total`；
3. `source_endpoint_E_G_minus_E_FUD`。

三者满足：

`pi_sigma_source_direct_total + orbital_response_total = source_endpoint_E_G_minus_E_FUD`。

0°端点在 `1.0e-8 Eh` 阈值内，标签为 `indeterminate_within_tolerance`。17°端点为正，标签为 `pi_sigma_source_endpoint_destabilizing_at_17deg_table_5_15_source_proxy`。

## 允许用途

该数据仅用于复核P05在冻结Table 5-15固定source-proxy 17°点的范围化结论，以及分析正直接项被负轨道响应部分抵消的机制。

## 禁止用途

- 不得作为生产ML训练标签；
- 不得用于MACE、PySR或工业级泛化；
- 不得宣称所有角度、所有NBA或所有分子的π–σ相互作用均为去稳定化；
- 不得将source非变分直接项替换为普通物理变分相互作用能。

每条记录均携带几何、LFMO基、源artifact、证书、计算配置、方法、基组、引擎、资源环境和公开来源的哈希或出处信息。

