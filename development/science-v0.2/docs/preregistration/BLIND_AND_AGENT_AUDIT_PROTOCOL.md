# 密封盲法与 Agent 审计协议

## 1. 角色

- `PROTOCOL_OWNER`：冻结 claim、estimand、输入和非目标性验收规则；
- `UNBLINDED_EVALUATOR`：唯一可读取 V0.1 目标值和比较规则的角色；
- `BLINDED_CALCULATION_AGENT`：只读取密封 bundle，禁用外网和完整仓库搜索；
- `REPLAY_AGENT`：从洁净克隆/容器按同一 bundle 重放，不能读取首轮结果。

同一 Agent 实例不能同时承担计算与揭盲角色。人在同一项目中兼任角色时，也必须使用两个独立工作目录和分开的输入 ACL。

## 2. 密封顺序

1. evaluator 生成只含坐标、方法、基组、状态、收敛门禁和输出 Schema 的 bundle；
2. 扫描 bundle，拒绝原著数值、V0.1 判定、比较方向和发布文案；
3. 记录 bundle SHA-256；
4. calculation agent 生成脚本，记录脚本 SHA-256 后才允许运行；
5. 首轮 raw/parsed 结果记录 SHA-256；
6. evaluator 才能挂载目标值并生成 comparison JSON；
7. 任何揭盲后的重跑必须标记 `POST_UNBLIND`，不能替代首轮盲结果。

## 3. 计算隔离

- 网络策略：`DENY`；
- 仓库策略：只挂载 bundle 和空输出目录，不挂载完整 AI4OrgChem；
- 环境：只读环境锁，scratch 单独挂载；
- 日志：命令、工作目录、退出码、输入/输出哈希和资源量必须保存；
- 失败：不得由 evaluator 暗示“目标应为正/负”后修改根或阈值。

## 4. Agent run bundle

每次运行必须满足 [`agent_run_bundle.schema.json`](../../configs/agent_run_bundle.schema.json)。提示正文如含受限信息不公开，只保存 SHA-256 和脱敏摘要。人工批准、参数选择、失败重试及停止原因必须显式记录。

`replay_status` 与 R1–R3 完全分离。外部 Agent 成功重放只提高可复现性；只有科学工作流和 Agent 工作流都端到端闭合时，才可从 M1+ 评估为 M2。

## 5. WP0 演练判定

WP0 只做无科学目标的打包/哈希/权限演练。演练通过不能被表述为完成了科学盲法，也不能授予 WP1–WP4 计算权限。
