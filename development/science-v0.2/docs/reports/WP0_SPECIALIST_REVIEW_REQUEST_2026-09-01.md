# Gate V2-0 专项复审请求

日期：2026-09-01  
提交状态：`INTERNAL_VALIDATION_PASS / GATE_NOT_PASSED`  
授权边界：WP1–WP4 均保持 `HOLD`

## 已通过且不要求重复审查

- V0.1 基线与 15 个结果文件哈希保持不变；
- 关系类型、比较结果、R1–R3、重放状态和 Agent 成熟度已经分轴；
- P09/P10/P12 已拆成 A/B 六个 estimand；
- WP2 八个核心锚点与 WP4-B 唯一主 estimand 已机器冻结；
- 非科学密封包演练、Agent 脱敏样例和环境隔离已通过；
- 专用单元测试和总验证器通过，科学作业数为 0；具体计数以验证器实时输出为准。

## 只需复审四项决策

### RQ-1：WP1 主锚点与活动空间

请确认或否决：

- 主锚点固定为 `selected-CI+PT2 extrapolation/cc-pVDZ`；
- `CCSDT/cc-pVDZ` 仅在主锚点不可获得或连续三次可审计资源失败时作为备用；
- `CAS(4,4)` 仅为最低空间，`CAS(12,12)` 为主敏感性候选；
- 两根等权 SA-CASSCF 用于路径跟踪，后相关主变体为 SC-NEVPT2。

当前事实：PySCF CASSCF/NEVPT2/selected-CI 接口存在；Quantum Package `v2.2.2`、提交 `0f320db735bfdbdf9861c9cad9f3f64175cc8c3c` 已作为唯一主锚点实现建立隔离环境并通过非 CBD 烟测。

实现决定：Quantum Package CIPSI+PT2 多点外推已接受；详见 `protocols/WP1_PRIMARY_ANCHOR_IMPLEMENTATION_CANDIDATE.md`。WP1 CBD 科学计算仍未授权。

判定：`ACCEPTED_AS_UNIQUE_PRIMARY_HIGH_LEVEL_ANCHOR_IMPLEMENTATION`  
意见：环境建立与非 CBD 烟测已完成，不构成 WP1 科学结果。

### RQ-2：WP3 模式分层

请确认或否决以下分层：

- Gate V2-0 冻结并验收 B2u/A1g/E2g 对称适配、质量加权骨架种子；
- Hessian 本征模及同不可约表示内的模式混合，在 WP3 获单独授权后作为 Gate V2-3 科学任务完成；
- 当前种子不得称为 Hessian 正常模，也不得据此宣称“核排斥主导”。

判定：`ACCEPTED_SEED_AT_V2_0_HESSIAN_AT_V2_3`  
意见：原始种子固定保留；Gate V2-3 比较简并/近简并本征子空间重叠或主角，不强制逐向量对应。

### RQ-3：WP3 唯一电子结构干预

请确认或否决：普通闭壳层 RKS 对照于冻结三个 Kekulé 片段的 2011-style conditional-SCF 屏蔽；以非正交投影和最大重叠跟踪 π 子空间；奇异值或根重叠低于 0.90 即失败；主因果量为 `Delta_k_e = k_e(localized)-k_e(ordinary)`。

判定：`ACCEPT / REVISE / REJECT`  
意见：

### RQ-4：WP4 双支路和先导集

请确认或否决：

- WP4-A 只报告 source-aligned CESE；
- WP4-B 主估计量固定为 ISE-II、0 K ZPVE 校正 ASE；
- 两支路默认 `INCOMPARABLE`，不得合并或投票；
- 先导集固定为 `8/10、16/18、32/34`；
- 构象搜索未达到停止标准时必须判为 `INDETERMINATE`。

判定：`ACCEPT / REVISE / REJECT`  
意见：

## 复审后授权规则

RQ-1 与 RQ-2 已接受；RQ-3、RQ-4 及其他剩余门禁仍待闭合。即使全部接受，也只表示 Gate V2-0 可以进入最终判定；仍须分别签发 WP1、WP2、WP3、WP4 启动授权。ORCA 许可/二进制未具备时 WP2 ORCA 支路继续 HOLD。任何复审意见不得要求改写 V0.1 历史结果。

## 核心附件

- `configs/science_v0.2/wp0_readiness.json`
- `configs/science_v0.2/claim_estimand_registry.json`
- `configs/science_v0.2/wp2_core_anchors.json`
- `configs/science_v0.2/wp3_symmetry_mode_seeds.json`
- `docs/releases/science_v0.2/protocols/WP1_WP4_EXECUTION_CONTRACTS.md`
- `docs/releases/science_v0.2/reports/WP0_IMPLEMENTATION_STATUS_2026-09-01.md`
