# WP0：Agent 审计与重放样例包

日期：2026-09-01  
状态：`内部样例 PASS；外部洁净重放未执行`  
科学证据等级：`不适用`

## 已实现

已生成 `runs/science_v0.2/wp0_agent_replay_sample/agent_run_bundle.json`，记录：

- 模型供应方、模型标识、日期和推理设置可见性；
- 系统提示与任务提示的 SHA-256，而不保存敏感提示正文；
- 工具调用、命令、补丁、人工干预、失败与重试；
- 结果—报告—Gate 的证据图及文件哈希；
- 环境锁文件及哈希；
- Quantum Package 构建补丁、隔离环境锁、失败重试和非 CBD 烟测记录；
- 自动脱敏扫描状态。

样例包通过 JSON Schema、敏感路径/API 密钥模式扫描以及引用文件哈希复核。

## 等级边界

本样例证明的是 Agent 审计数据结构可以生成并由机器核验，不等于外部重放已经完成：

- `replay_status` 仍为 `NOT_REPLAYED`；
- Agent 成熟度仍为 `M1_PLUS`；
- 不改变任何 R1–R3 科学证据等级；
- 不授权 WP1–WP4 科学计算；
- 后续只有在独立洁净环境由不同重放角色成功执行后，才可登记 `EXTERNAL_CLEAN_REPLAY`。
