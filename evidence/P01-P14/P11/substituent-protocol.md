> **Current-evidence note (2026-09-08):** This source-2007 planar restricted-optimization protocol supersedes the earlier fixed-geometry proxy for the P11-B CE/IE classification. The fixed-proxy result remains in project history for audit.

# P11-B 取代苯共轭/诱导效应分离协议 v0.2

- 协议ID：`p11-source2007-planar-recalculation/0.2`
- 对象：单一氰基苯与同协议苯锚点
- 方法：PySCF B3LYP/6-31G(d)，闭壳层RKS，grid level 3
- 原著方法版本：Bao–Yu 2007定义
- 原著程序代码：未使用

## 1. 可证伪命题与公式

`ESE(SB) = (E_G-E_GLI) - sum(i=1..3; E_GEi-E_GLI)`

`ESE(Ph) = (E_GE7-E_GLII) - sum(i=4..6; E_GEi-E_GLII)`

`ESE(Bz) = (E_G-E_GL) - 3(E_GE1-E_GL)`

`CE = ESE(SB) - ESE(Ph)`

`IE = ESE(Ph) - ESE(Bz)`

原著对氰基苯给出的约值为：`ESE(SB)=-37.3`、`ESE(Ph)=-38.5`、`ESE(Bz)=-39.0`、`CE=+1.2`、`IE=+0.49 kcal/mol`。

## 2. source-2007电子结构语义

- 每次SCF迭代将不同局域π片段之间的AO Fock与overlap块置零；
- 不删除双电子积分；
- 保留物理一电子算符，不把hcore额外置零；
- 氰基苯使用G、GL-I、GE1–GE3、GL-II、GE4–GE7共10态；苯使用G、GL、GE1共3态。

## 3. 全平面逐状态受限优化

- 所有13个G/GL/GE状态分别优化，不在同一固定几何上比较；
- 每个原子的Cartesian `z`均硬冻结为0，只优化平面内自由度；
- geomeTRIC 1.1.1调用解析conditional-RKS梯度；
- 收敛阈值：能量`1e-6 Eh`、梯度RMS/最大值`3e-4/4.5e-4 Eh/Bohr`、位移RMS/最大值`1.2e-3/1.8e-3 Å`。

氰基苯从Figure 7公开的逐态重原子键长重构结构出发；苯从2007 Supporting Information结构出发。Figure 7未公开完整Cartesian和氢坐标，因此本项目不声称原厂坐标逐点相同。

## 4. 验收与已声明诊断偏差

阻断条件包括：13态全部优化/SCF收敛、最大面外偏差不超过`1e-10 Å`、三个ESE及CE/IE在冻结容差内、CE/IE为正、`|ESE(Ph)|<|ESE(Bz)|`。

初始协议另设“任一环键相对Figure 7/SI起始值变化不超过`0.001 Å`”的source-start诊断。观察最大值为`0.002328 Å`（氰基苯G态），故该诊断明确记录为未满足，阈值没有事后放宽。由于输入只含四舍五入的重原子键长而非完整坐标，该诊断用于披露重构敏感性，不替代优化收敛、平面性或ESE/CE/IE估计量验收。

## 5. 边界

结论只适用于单一氰基苯、source-2007条件态定义和上述全平面受限优化协议。不外推一般Hammett关系、其他取代基或方法无关定律；不生成AI训练标签。
