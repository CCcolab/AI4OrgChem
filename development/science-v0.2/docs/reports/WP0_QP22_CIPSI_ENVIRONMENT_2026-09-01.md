# WP0 Quantum Package/CIPSI 隔离环境与非 CBD 烟测记录

- 日期：2026-09-01
- 环境：`ai4orgchem-v02-cipsi`（WSL2 `Ubuntu-24.04`）
- 状态：`PROVISIONED_AND_NON_CBD_SMOKE_VERIFIED`
- 分类：环境、构建及玩具烟测；不是 WP1 科学计算
- CBD 输入/结果：`0`
- WP3 Hessian：`0`

## 实现身份

WP1 唯一主高等级锚点实现已接受为 Quantum Package 的 CIPSI+PT2。为避免“2.2”这一简称掩盖上游标识差异，本环境使用复合身份：

| 字段 | 冻结值 |
|---|---|
| 上游标签 | `v2.2.2` |
| 完整提交 SHA | `0f320db735bfdbdf9861c9cad9f3f64175cc8c3c` |
| 源码内部 `VERSION` | `2.3.1` |
| 官方源码归档 SHA-256 | `10cc6e0860092b937cd9b142b60a22b057632f013f7ef68b54164ef12e03e307` |
| 未修补源码树 SHA-256 | `5820e7fdfa2f5ef8e243e75966e45a7d46210a897cbe771038c3dca088798559` |
| EZFIO | `dba01c4fe0ff7b84c5ecfb1c7c77ec68781311b3` |
| IRPF90 | `4ab1b175fc7ed0d96c1912f13dc53579b24157a6` |
| `qp2-dependencies` gitlink | `e0d0e02e9f5ece138d1520106954a881ab0b8db2` |
| 许可证 | AGPL-3.0；未复制源代码或二进制到 Apache-2.0 发布包 |

上游标签与源码内部版本号不一致是被记录的上游事实，不通过重命名消除。后续每个 WP1 结果必须同时引用标签、提交和内部版本。

## 隔离构建栈

| 组件 | 版本 |
|---|---:|
| GCC / GFortran | 13.4.0 |
| OCaml | 4.14.2 |
| OPAM | 2.1.3 |
| Python | 3.10.21 |
| OpenBLAS | 0.3.34 |
| ZeroMQ / f77_zmq | 4.3.5 / 4.3.3 |
| TREXIO | 2.3.2 |
| Bats | 1.14.0 |

初始 GCC 9 + OCaml 4.11 路线在 OCaml 链接阶段因 `__secure_getenv` 失败。该失败没有被掩盖，也没有修改旧环境；最终改用隔离环境内 GCC/GFortran 13.4.0 和 OCaml 4.14.2。完整 Conda、显式包、OPAM 与 pip 锁分别保存在 `locks/science_v0.2/`。

为阻止构建过程拉取可变的子模块，只应用了 `offline-pinned-submodules.patch`：它验证 EZFIO/IRPF90 精确提交并跳过对 `qp2-dependencies` 的 `master` 更新，不改动任何能量、行列式选择、PT2 或外推算法。烟测编译配置只用于 WP0 构建验证，不是 WP1 科学协议。

## 构建产物身份

| 产物 | SHA-256 |
|---|---|
| `src/fci/fci` | `bdb1a32e81e5ece5ca7609c8be477f3406a7174ef98c0fa50173f05f32de613f` |
| `src/hartree_fock/scf` | `68a0f9f7dbb9e56149d50efe6b6d92fbbe7071c400b639ae2d8c26c5826f54f6` |
| `ocaml/qp_run` | `2a742dcb9b9a6b7cdd3f0b119be8a238a48b8612749423a649afba07ac700ae7` |

动态链接检查确认主要科学库来自该隔离环境，包括 OpenBLAS、TREXIO、f77_zmq、ZeroMQ、GFortran、libgomp、HDF5 与相关运行库。

## 上游非 CBD 烟测

执行官方上游 `H2_1` 与拉伸 `B-B` Bats 夹具，各自依次通过 EZFIO 建立、HF 和 FCI/CIPSI+PT2，共 6 项通过。

| 夹具 | HF / Eh | `E_var` / Eh | `E_var+PT2` / Eh | 行列式数 | 结果 |
|---|---:|---:|---:|---:|---|
| H2 | -1.00592496328853 | -1.06415255208430 | -1.06415255208430 | 32 | PASS |
| 拉伸 B2 | -48.9950585433336 | -49.1407763998013 | -49.1409947621282 | 12067 | PASS |

拉伸 B2 的官方校正能参考为 `-49.14103054419 Eh`，容差 `3e-4 Eh`，本次结果在容差内。源代码中随机 PT2 初始化为 `seed(i)=i`；未来 WP1 科学运行仍必须逐作业记录随机种子、PT2 统计误差、方差和外推序列。

## 边界结论

本记录只关闭“主锚点实现是否可在隔离环境中构建并执行 CIPSI+PT2”的工程问题。它不证明 CBD 的活动空间、根跟踪、外推稳定性或科学结论，也不提高任何 V0.1 命题的证据等级。

```text
WP1_PRIMARY_ANCHOR_QP22_CIPSI_PT2: ACCEPTED
QP22_CIPSI_ENVIRONMENT: PROVISIONED_AND_NON_CBD_SMOKE_VERIFIED
AUTHORIZATION_AT_SMOKE_EXECUTION: WP1_NOT_AUTHORIZED / WP3_HESSIAN_NOT_AUTHORIZED
CURRENT_AUTHORIZATION: SEE configs/science_v0.2/wp_authorizations.json
GATE_V2_0_CURRENT: PASSED
```

上述烟测记录中的`authorization`字段冻结的是烟测执行时状态，不被后续授权回写。当前状态为WP1、WP3已授权但尚未启动科学作业。
