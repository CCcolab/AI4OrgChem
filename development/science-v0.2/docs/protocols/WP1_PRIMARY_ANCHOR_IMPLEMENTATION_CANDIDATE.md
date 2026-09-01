# WP1 主高等级锚点实现决定与环境记录

状态：`ACCEPTED / ENVIRONMENT_PROVISIONED / NON_CBD_SMOKE_PASS / WP1_AUTHORIZED_NOT_STARTED`
日期：2026-09-01

## 决策建议

已接受 **Quantum Package v2.2.2、提交 `0f320db735bfdbdf9861c9cad9f3f64175cc8c3c` 的 CIPSI+PT2 外推**作为 WP1 selected-CI 唯一主高等级锚点实现。该源码内部 `VERSION` 为 `2.3.1`，因此所有记录必须同时保留标签、提交和内部版本。PySCF 2.14 的 CASSCF/SC-NEVPT2 继续作为活动空间与方法敏感性支路，不以 PySCF 内置 `fci.selected_ci` 冒充主锚点。

## 技术依据

- Quantum Package 的 CIPSI 迭代同时记录变分 selected-CI 能量和 PT2 修正，并对 `E_var`–`E_PT2` 进行多点 FCI 外推；这与预注册主锚点要求直接对应；
- PySCF 内置 selected-CI 接口可用于有限空间求解和实现检查，但当前接口探测没有发现等价的外部 PT2 多点外推工作流；
- Dice/SHCI 同样具备半随机 PT2，但需要单独编译 Dice、安装 `shciscf` 并维护运行路径，当前不作为首选，避免在 WP0 同时维护两个 selected-CI 实现；
- PySCF CASSCF/SC-NEVPT2 接口已经可用，适合作为活动空间和后相关敏感性层，而不是 CIPSI 主锚点替代品。

## 冻结候选合同

- 程序：Quantum Package `v2.2.2`，提交 `0f320db735bfdbdf9861c9cad9f3f64175cc8c3c`，源码内部版本 `2.3.1`；
- 主方法：冻结 C 1s 的 CIPSI，报告每次迭代的 `E_var`、`E_PT2`、`E_var+E_PT2`、行列式数和统计误差；
- 外推：按官方多点外推输出，至少比较最后 2–7 点；只有斜率/截距与点数选择稳定时才给出主锚点；
- 基组：`cc-pVDZ`；
- 几何：预注册 D2h 最低点、D4h 驻点和冻结自动异构化路径；
- 主量：`Delta_E_auto = E_S0(D4h)-E_S0(D2h)`；
- 主误差：两个端点外推不确定度按独立误差传播，并单独报告随机 PT2 误差；
- 失败：PT2 外推不稳定、状态/根身份不连续、资源越界或程序构建失败均登记为 `INDETERMINATE`，不得改用更接近目标值的设置。

## 环境与许可证边界

Quantum Package 2.2 使用 AGPL-3.0。它只安装在独立 WSL 环境或容器中，不把源代码、二进制或依赖复制进 Apache-2.0 项目发布包。公开仓库只保存版本/提交、输入合同、命令摘要、哈希、解析器和依法可发布的输出。

隔离环境名：`ai4orgchem-v02-cipsi`。环境已建立并通过官方 H2 与拉伸 B2 非 CBD 烟测；完整记录见 `../reports/WP0_QP22_CIPSI_ENVIRONMENT_2026-09-01.md`。安装、源代码和二进制不进入 Apache-2.0 GitHub 发布包。

### 本机只读依赖清点

专用环境已锁定 GCC/GFortran 13.4.0、OCaml 4.14.2、OPAM 2.1.3、OpenBLAS 0.3.34、ZeroMQ 4.3.5、f77_zmq 4.3.3 和 TREXIO 2.3.2。构建使用只处理依赖固定的可审计补丁，不修改科学算法。既有 `ai4orgchem`、`ai4orgchem-nequip` 和 `ai4orgchem-v02-qm-open` 未被修改。

环境验证不等于科学协议验证。WP1现已获得独立启动授权，但CBD输入、活动空间、根跟踪、CIPSI/PT2外推序列和WP1结果仍未运行；首个作业前必须先冻结并密封科学输入包。

## 已记录决定

1. Quantum Package CIPSI+PT2：`ACCEPTED_AS_UNIQUE_PRIMARY_HIGH_LEVEL_ANCHOR_IMPLEMENTATION`；
2. Dice/SHCI：仅为未来可选交叉检查，不是 WP1 必做支路；
3. PySCF CASSCF/SC-NEVPT2：敏感性与诊断支路，不承担主锚点身份；
4. WP1 科学计算：`AUTHORIZED_TO_START / NOT_STARTED`。

## 官方依据

- Quantum Package：<https://github.com/QuantumPackage/qp2>
- CIPSI/PT2 与外推文档：<https://quantum-package.readthedocs.io/en/master/modules/cipsi.html>
- PySCF SHCI 接口：<https://pyscf.org/interface/shciscf.html>
