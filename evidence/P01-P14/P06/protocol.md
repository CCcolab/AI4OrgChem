> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P06 Target B范围化非键σ–σ判定协议 v0.1

- 日期：2026-08-20
- 命题：P06
- Target：B
- 状态：范围化科学发布协议
- 原著程序代码：未使用

## 1. 唯一观测量

在冻结的Table 5-19 source-geometry candidate中定义：

`Delta E_sigma_sigma(theta) = E_PDSI(theta) - E_FUL(theta)`。

FUL保持bonded-σ A与P=(B+C)相互隔离；PDSI只释放这两个bonded-σ分组之间的隔离。π分组和cut-σ分组不变。因此：

- `Delta E_sigma_sigma > +1.0e-8 Eh`：释放该隔离使source-defined状态能升高，非键σ–σ净端点为去稳定化；
- `Delta E_sigma_sigma < -1.0e-8 Eh`：净端点为稳定化；
- 其余：容差内不能判定。

该符号解释仅适用于原著FUL-2/PDSI非变分源定义，不等同于普通RHF变分相互作用能或经典位阻能。

## 2. 冻结受测域

- 分子：parent N-benzylideneaniline source-geometry candidate；
- 几何：约束B3LYPG/6-311G(d,p)的0°与17°点；
- 单点：RHF/STO-3G；
- 状态：FUL-2/2F-2S与PDSI；
- 能量复核：PySCF AO积分加独立NumPy RHF J/K组装；
- 原著对应：Figure 5-11、Scheme 5-5、Table 5-19。

不增加分子、角度、基组或电子状态，不宣称历史Cartesian坐标完全一致。

## 3. 状态能量恒等式

每个点必须满足：

`E_PDSI(independent) - E_FUL(independent) = Delta E_sigma_sigma`

闭合容差为 `1.0e-9 Eh`，并要求与Table 5-19数值的绝对误差不超过 `0.010 Eh`。

## 4. 最终范围化判定

- 0°：`E_PDSI-E_FUL = +0.067957103709 Eh`；
- 17°：`E_PDSI-E_FUL = +0.062753624288 Eh`。

两个端点均为正，且17°比0°降低约 `0.005203479422 Eh`。因此，在冻结的Table 5-19两个source-proxy点中，source-defined非键σ–σ端点均表现为去稳定化，扭转后该正端点幅度减小。

## 5. 禁止外推

本协议不授权：

- 将结果直接称为所有分子的“位阻排斥能”；
- 所有角度、所有NBA或所有σ–σ相互作用的普遍定律；
- 与Target A/C的不同方法、基组和状态能量直接相加；
- 生产ML标签、MACE/PySR训练或工业级泛化；
- 在P07完成前声称已经形成三分量统一总能量。

