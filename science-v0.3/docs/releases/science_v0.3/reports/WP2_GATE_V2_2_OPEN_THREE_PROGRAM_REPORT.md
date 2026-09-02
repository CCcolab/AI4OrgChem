# WP2 / Gate V2-2 开源三程序复算整改报告

- 日期：2026-09-02
- 状态：`PASSED_OPEN_THREE_PROGRAM`
- 科学问题状态：`RESOLVED_WITHIN_FROZEN_OPEN_THREE_PROGRAM_ESTIMAND`
- 原 ORCA 专用支路：`NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE`
- 对 V0.1 十四项结论的影响：不改写，只提升普通态跨程序复算证据
- 对 V0.2.0 的影响：不覆盖、不回写，V0.2.0 保持不可变历史发布

## 1. 整改目标

WP2 要检验的是：在同一冻结几何、同一 Gaussian-style B3LYP、同一球谐基组、无经验色散、无密度拟合的条件下，独立量子化学程序能否重现关键普通态的总能量与一阶导数。

V0.2 历史支路未通过，主要有两个原因：

1. 本机没有经许可的 ORCA 可执行文件；
2. 旧 Psi4 运行把 `DIRECT` 的默认 DF 预迭代误判为无法执行无 DF 路径，同时各程序的 DFT 网格没有收敛到共同精度。

本次整改不把 NWChem 冒充 ORCA。它建立一条独立、明确标注为 `COMPLEMENTARY` 的开源三程序支路：PySCF 2.14.0、Psi4 1.11、NWChem 7.3.0（revision 3272822；conda 包 7.3.1）。

## 2. 关键技术修正

### 2.1 同一估计量

三程序均使用：

- Gaussian-style B3LYP：20% HF、80% Slater、72% B88、19% VWN1-RPA、81% LYP；
- 球谐 6-31G(d) 或 6-311G(d,p)；
- C1、固定电荷/多重度、不重定向；
- 冻结 bohr 坐标，避免程序各自 Å→bohr 常数造成内部几何差异；
- 无 D3/D4 等经验色散；
- 无 RI/DF，精确直接二电子积分。

NWChem 的 B3LYP 组成和 `direct`/网格语义见其[官方 DFT 文档](https://nwchemgit.github.io/Density-Functional-Theory-for-Molecules.html)。Psi4 官方文档说明 `DIRECT` 默认可先做 DF 轨道预收敛，因此本次显式设置 `DF_SCF_GUESS=false`，并由日志中的 `SCF Algorithm Type is DIRECT`、`@RKS` 和 `DirectJKGrad` 验证实际路径；参见 [Psi4 SCF 文档](https://psicode.org/psi4manual/master/scf.html)。

### 2.2 网格收敛

旧的 PySCF level 3、Psi4 75×302 与 NWChem 默认网格不能作为严格绝对能量比较。整改后采用：

- PySCF：H 300×1202；C/N/O 300×1454，`nwchem_prune`；
- Psi4：300×1454，ROBUST pruning；
- NWChem：官方 `huge` 网格，并要求输出证明实际采用。

苯校准的三程序最大能量差为 `1.7427×10^-9 Eh`，说明功能定义和高网格估计量已对齐。

## 3. 八个核心锚点

| 锚点 | 观测量 | 三程序最大能量跨度 / Eh | 导数差 | 结果 |
|---|---|---:|---:|---|
| P03 NBA 0° | 能量、扭转投影力 | 1.7238×10^-8 | 投影导数跨度 1.7854×10^-14 Eh/bohr | 通过 |
| P03 NBA 60° | 能量 | 1.7607×10^-8 | — | 通过 |
| P08 丁二烯 G | 能量、完整梯度 | 1.8995×10^-8 | 最大 RMS 3.7022×10^-7 Eh/bohr | 通过 |
| P09 苯 G | 能量 | 1.7378×10^-9 | — | 通过 |
| P09 环丁二烯 G | 能量 | 7.5090×10^-9 | — | 通过 |
| P10 苯 B2u Q0 | 能量、投影力 | 1.7057×10^-9 | 投影导数跨度 1.3627×10^-13 Eh/bohr | 通过 |
| P10 苯 B2u Q+ | 能量 | 1.0990×10^-9 | — | 通过 |
| P11 呋喃 G | 能量 | 1.1508×10^-8 | — | 通过 |

预注册门槛为：绝对能量 `5×10^-6 Eh`，完整梯度 RMS `5×10^-5 Eh/bohr`。8/8 锚点全部通过。

## 4. 相对能量

| 能量差 | PySCF | Psi4 | NWChem | 跨程序跨度 | 门槛 | 结果 |
|---|---:|---:|---:|---:|---:|---|
| P03 60°−0° / kcal mol^-1 | -0.63131335 | -0.63133442 | -0.63132511 | 2.1067×10^-5 | 0.05 | 通过 |
| P10 Q+−Q0 / kcal mol^-1 | 0.21110543 | 0.21110477 | 0.21110550 | 7.2854×10^-7 | 0.05 | 通过 |

2/2 相对能量对全部通过。

## 5. Gate 判定

开源三程序支路的 Gate V2-2 判定为 `PASSED_OPEN_THREE_PROGRAM`。这意味着 WP2 的“独立程序是否能在同一估计量上重现关键普通态能量和一阶导数”已经得到肯定回答。

该判定不等于：

- 已执行 ORCA；
- NWChem 与 ORCA 等价；
- 普通态 B3LYP 复算就是 LFMO/DSI/FUD 自定义态历史复现；
- WP2 自动改变 V0.1 的十四项命题分类。

原 ORCA 专用支路保持 `NOT_ESTABLISHED_NO_LICENSED_EXECUTABLE`。这是程序许可/可用性边界，不再阻止开源三程序支路形成独立科学证据。

## 6. 可复核入口

- 冻结合同：`configs/science_v0.3/wp2_open_three_program_contract.json`
- 运行器：`scripts/science_v0.3/run_wp2_open_three_program_lane.py`
- 汇总器：`scripts/science_v0.3/summarize_wp2_open_three_program_gate.py`
- 机器汇总：`data/science_v0.3/processed/wp2/wp2_open_three_program_summary.json`
- 八份可发布锚点记录：`data/science_v0.3/raw/wp2/anchors/`
- Gate 决定：`data/science_v0.3/decisions/wp2/gate_v2_2_open_lane_decision.json`
- NWChem 环境锁：`locks/science_v0.3/ai4orgchem-v02-wp2.environment.yml` 与 `.explicit.txt`
- 原始本地运行记录：`runs/science_v0.3/wp2/open_three_program/`

复算单个锚点的入口：

```bash
python scripts/science_v0.3/run_wp2_open_three_program_lane.py \
  --anchor WP2-P08-BUTADIENE-G-EG
```

汇总入口：

```bash
python scripts/science_v0.3/summarize_wp2_open_three_program_gate.py
```
