# Science V0.2 WP0 实施状态

- 日期：2026-09-01
- 总状态：`IN_PROGRESS_NOT_PASSED`
- 科学作业：`0`
- V0.1 改写：`0`

## 已完成

1. 冻结公开维护基线 `main@032027e`、6 个 V0.1 标签、公开 manifest 及 15 个 P01–P14 结果文件 SHA-256；
2. 建立双轴证据 Schema；反向证据固定编码为 `SAME_ESTIMAND + OPPOSED`；
3. 将 P09、P10、P12 拆为 A/B 六个机器可读 claim/estimand；
4. 将 R1–R3、`replay_status`、M1+/M2 分为三条独立轴，并禁止 P10-B 自动升级 P10-A；
5. 冻结 WP1 selected-CI+PT2 主锚点及 CCSDT 备用条件；
6. 冻结 WP2 八个三程序核心锚点；
7. 冻结 WP3 的 B2u/A1g/E2g 坐标和唯一 conditional-SCF π 局域干预；
8. 生成 WP3 质量加权骨架种子；归一化、正交、刚体投影、不可约表示及 E2g 子空间检查全部通过；
9. 冻结 WP4-B 的 0 K ZPVE 校正 ISE-II ASE 和 `8/10、16/18、32/34` 配对先导集；
10. 完成一次非科学密封包三哈希演练，并以 WSL 用户/mount/network namespace 验证无路由、无非回环地址、完整仓库遮蔽及 bundle-only；
11. 建立 Agent run bundle Schema和脱敏样例，Schema、正例、应拒绝负例、敏感信息扫描与引用哈希全部通过；
12. 完成 WSL2/硬件/既有环境只读清单，未改动 `ai4orgchem` 与 `ai4orgchem-nequip`；
13. 创建并锁定 `ai4orgchem-v02-qm-open`；Psi4 1.11 与 PySCF 2.14.0 导入通过；
14. 完成 WP1 无分子接口探测：CASSCF、NEVPT2、PySCF selected-CI 接口存在，并明确它们不替代 CIPSI+PT2 主锚点；
15. 接受 Quantum Package `v2.2.2`、提交 `0f320db735bfdbdf9861c9cad9f3f64175cc8c3c`（源码内部 `VERSION=2.3.1`）为 WP1 唯一主高等级锚点实现；
16. 创建隔离的 `ai4orgchem-v02-cipsi` 环境，锁定编译器、Conda、OPAM 与 pip 依赖，未修改既有环境；
17. 完成 Quantum Package 构建，并以官方 H2 和拉伸 B2 夹具通过 EZFIO、HF、FCI/CIPSI+PT2 共 6 项非 CBD 烟测；
18. 冻结 WP3 对称适配种子用于 Gate V2-0，Hessian 本征模与简并子空间比较明确延后至获授权的 Gate V2-3；
19. 专用测试与 WP0 总验证器均通过、0 失败；具体数量以验证器实时输出为准。

## 机器验证结果

```text
validator_status = PASS
gate_status      = IN_PROGRESS_NOT_PASSED
science_jobs     = 0
unit_tests       = 9 PASS
validator_checks = 23 PASS
```

验证器 PASS 只说明当前基线、Schema、协议、样例和哈希自洽，不代表 Gate V2-0 已经通过，更不授权 WP1–WP4 科学作业。

## 未闭合项

| 项目 | 当前状态 | 为什么不能由内部实现直接关闭 |
|---|---|---|
| WP1 主高等级锚点环境 | `QP22_CIPSI_PROVISIONED / NON_CBD_SMOKE_PASS` | 仅关闭实现与运行时缺口；CBD 协议和科学结果尚未获授权 |
| ORCA 支路 | `NOT_FOUND_LICENSE_REQUIRED` | 需要用户依法取得并安装受许可二进制；不得由项目分发 |
| WP3 模式身份 | `V2_0_SEED_ACCEPTED / V2_3_HESSIAN_NOT_AUTHORIZED` | 当前向量是冻结的对称适配种子；不得称为 Hessian 本征正常模，也不得事后替换 |
| 剩余科学合同专项复审 | `PENDING` | 已接受 WP1 实现与 WP3 Gate 拆分；WP4 及其余合同项仍须按门禁完成 |
| 外部洁净重放 | `NOT_REPLAYED` | 当前仅有内部脱敏样例，不能宣称 M2 |
| WP1–WP4 启动授权 | `NOT_GRANTED` | Gate 通过也不自动授权后续科学计算 |

## 下一步

继续完成剩余 Gate V2-0 合同和跨程序就绪项。Quantum Package/CIPSI 环境建立已完成，但不得据此启动 CBD。当前仍不安装或分发受许可 ORCA，不运行 CBD、苯 Hessian/干预或大轮烯科学计算；WP1、WP3 和其他后续工作包均需独立授权。
