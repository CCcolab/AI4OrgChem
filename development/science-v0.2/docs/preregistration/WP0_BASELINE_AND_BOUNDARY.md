# Science V0.2 WP0 基线与执行边界

- 预注册时点状态：`IN_PROGRESS_NOT_PASSED`
- 当前状态入口：`configs/science_v0.2/wp0_gate_final_decision.json`（Gate 已通过）与 `configs/science_v0.2/wp_authorizations.json`（WP1/WP3 已单独授权）
- 日期：2026-09-01
- 本文件记录预注册时点授权：当时只执行WP0。当前授权以后续`wp0_gate_final_decision.json`和`wp_authorizations.json`为准。
- V0.1 维护基线：公开仓库 `main@032027e80edc779fdd0860df869272b36aaf660e`。

## 1. 本次实际实施内容

WP0 只建立以下对象：V0.1 哈希快照、双轴证据模型、P09/P10/P12 A/B 命题拆分、盲法输入包协议、Agent 审计 Schema、WP1–WP4 执行前合同、环境和资源清单、机器验证器。

本阶段不运行 CBD 多参考、ORCA/Psi4、苯 Hessian/机制或轮烯构象计算；也不生成 V0.2 科学结论、生产标签或 Release Candidate。

## 2. V0.1 不可破坏合同

V0.1 的 15 个结果文件（P11 含两个子结果）、公开清单、历史标签及 Release 均只读。完整路径、大小和 SHA-256 见 [`configs/science_v0.2/v0.1_baseline.json`](../../configs/v0.1_baseline.json)。V0.2 只能新增证据，不得覆盖历史 JSON。

## 3. 证据身份

可比关系只允许 `SAME_ESTIMAND / COMPLEMENTARY / INCOMPARABLE`；比较结果单独使用 `CONSISTENT / PARTIALLY_CONSISTENT / OPPOSED / NOT_APPLICABLE`。真正反向结果写作 `SAME_ESTIMAND + OPPOSED`。

科学等级只使用 R1–R3；Agent 重放另用 `replay_status`，Agent 工程成熟度另用 M1+/M2。P10-B 可凭自身机制实验达到 R3，但不能据此自动升级 P10-A。

## 4. 当前未闭合项

1. 密封盲法包尚未完成隔离演练；
2. 三套 V0.2 专用环境尚未创建，现有 `ai4orgchem` 和 `ai4orgchem-nequip` 明确只读保护；
3. 本条记录的是预注册时点状态：当时 Psi4、ORCA 和 selected-CI 主锚点尚未配置；当前状态以后续 WP0 环境报告为准，其中 Psi4 与 Quantum Package/CIPSI 环境已建立，ORCA 仍未配置；
4. WP3 模式向量生成器尚未通过对称性与质量加权测试；
5. WP1、WP3、WP4 专项协议仍需复审；
6. 本条为预注册时点事实；后续WP1、WP3已获独立启动授权，WP2、WP4仍HOLD。

因此在本预注册快照形成时Gate V2-0不能写为PASS；后续最终判定已在全部门禁证据闭合后另行登记，不回写本文件的历史语义。
