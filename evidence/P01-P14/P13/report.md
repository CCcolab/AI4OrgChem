> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P13多环苯系烃范围化论证报告

- 协议：`p13-polycyclic-benzenoid/0.1`
- 原著程序代码：未使用。
- 历史限制几何优化：未宣称复现。
- 独立通道：项目自编写完美匹配枚举器加RDKit分子式校验。
- 证据身份：**图论枚举与公开能量账本复核；不是所有候选结构的独立量子化学重优化**

## 独立Kekulé图枚举

| 并苯环数 | 分子式 | Kekulé候选数 | GL合格候选数 |
|---:|---|---:|---:|
| 2 | `C10H8` | 3 | 1 |
| 3 | `C14H10` | 4 | 2 |
| 4 | `C18H12` | 5 | 3 |
| 5 | `C22H14` | 6 | 4 |
| 6 | `C26H16` | 7 | 5 |
| 7 | `C30H18` | 8 | 6 |

独立枚举得到Kekulé候选数为环数加1；去掉两个不满足GL六元组条件的端点型候选后，合格数为环数减1。

## 能量账本与规则冲突留出

- Table 7-1候选账本行数：14；所有ESE/CESE恒等式均在印刷精度内闭合。
- 萘至并六苯的源选定候选均满足GL规则，并且在合格候选内具有最高分子能量。
- `7-6-(4:0)`中，全体候选的最高能量结构具有N_GL=5、N_db=3，违反GL规则；过滤后原著选定的N_GL=4候选成为合格集合中的最高能量结构。
- 这证明能量规则不能脱离GL六元组规则单独使用。

## 范围化结论

- 公开数值支持局域增量账本、CESE/π尺寸趋势和规则层级的内部一致性。
- 独立图枚举支持GL候选筛选的组合拓扑基础。
- 由于没有重新执行原著2007限制几何优化，具体ESE/CESE数值仍属于源数值重构，而不是独立量化复现。

最终判定：`P13_CONSISTENT_IN_TESTED_RULE_HIERARCHY_AND_PUBLISHED_LEDGER_SCOPE`。

最准确表述是：**在已测试的GL规则层级与公开PBH能量账本范围内，P13与原著一致。未执行全部历史限制几何优化仅作为证据层级说明。**

本结果不是生产标签，不进入AI训练。

V0.2若继续增强，只选择少量预注册代表结构做盲重优化并报告排序变化与漏检风险；该新增通道不覆盖当前规则层级与账本范围内的一致判定。

## 自动检查

- `PASS` published_ESE_identities_close
- `PASS` published_CESE_identities_close
- `PASS` source_selected_acene_candidates_obey_filtered_energy_rule
- `PASS` acene_CESE_per_pi_matches_printed_values
- `PASS` acene_absolute_CESE_per_pi_decreases_with_size
- `PASS` all_scoped_CESE_per_pi_below_benzene_reference
- `PASS` all_scoped_adjacent_increment_sums_destabilizing
- `PASS` independent_graph_kekule_counts_match
- `PASS` independent_graph_GL_qualified_counts_match
- `PASS` independent_RDKit_formulas_match
- `PASS` holdout_detects_energy_rule_without_GL_filter_failure
- `PASS` holdout_source_selection_is_highest_energy_after_GL_filter
- `PASS` historical_quantum_program_not_claimed
- `PASS` production_label_disabled
- `PASS` AI_training_disabled
