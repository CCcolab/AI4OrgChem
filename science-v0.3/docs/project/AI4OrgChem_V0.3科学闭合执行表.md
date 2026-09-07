# AI4OrgChem V0.3.0 科学闭合执行表

- 执行原则：严格按序；前项形成机器判定后才进入后项。
- 版本原则：V0.1.0、V0.2.0 保持不可变；V0.3.0 只新增证据，不回写历史发布。
- 科学原则：`SAME_ESTIMAND` 才能直接升级原命题证据；互补估计量分别终判。

| 顺序 | 工作包 | 必须交付 | 当前状态 | 是否允许进入下一项 |
|---:|---|---|---|---|
| 1 | WP1：环丁二烯多参考锚点 | CIPSI+PT2主锚点、多参考敏感性、Gate V2-1 | `PASS_WITH_METHOD_SENSITIVITY` | 是 |
| 2 | WP2：跨程序普通态复算 | PySCF/Psi4/NWChem开放三程序8锚点、Gate V2-2 | `PASSED_OPEN_THREE_PROGRAM_LANE` | 是 |
| 3 | WP3：苯D6h机制 | Hessian模式、对称坐标、电子干预；P10-A/P10-B分判 | `PASSED`；P10-A=R2，P10-B=R3 | 是 |
| 4 | WP4-A：source-aligned CESE | 同估计量账本、公式闭合、与WP4-B隔离 | `CLOSED_SOURCE_ALIGNED_R1` | 是 |
| 5 | WP4-B：physical-state ASE | 8/10、16/18、32/34双来源实际计算、最低构象、0 K ASE、Gate V2-4P | `PASSED`；六点ASE、构象覆盖、最低点、Hessian/ZPVE及BS检查均闭合，机器验证通过 | 是 |
| 6 | WP5：独立Agent重放 | 外部洁净环境量化重跑、哈希比对、`replay_status`与M2 | `PASSED`；`EXTERNAL_CLEAN_REPLAY / M2`，绝对能量差`2.84e-13 Eh` | 是 |
| 7 | WP6：V0.3.0整合发布 | 七项状态矩阵、证据清单、复现包、安全检查、Release | `RELEASE_PACKAGE_READY`；280文件本地暂存包、SHA-256清单、安全扫描、23项项目合同测试及3项包内复算测试通过；远程Tag/Release待发布 | 是（仅允许发布） |

## 当前唯一执行项

科学计算和本地发布前全面复核已经结束。当前只允许固定最终提交哈希、创建远程`v0.3.0` Tag与GitHub Release，并执行标签后洁净克隆复验；不得新增分子、尺寸、构象、方法、基组或改写P01-P14既有分类。
