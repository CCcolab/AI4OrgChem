> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P07 LFMO核心多分量机制数据卡 v0.2

## 当前证据身份（2026-09-08）

P07现由两层证据共同支持：

1. P04–P06冻结结论的命题级综合；
2. 对既有五状态QM结果开展的独立同哈密顿量状态路径审计。

因此当前证据身份为`INDEPENDENT_COMPUTATIONAL_AUDIT_PLUS_DERIVED_SYNTHESIS`，不再是纯`DERIVED`。审计没有启动新QM计算：它在diphenyl imine parent NBA的0°/17°两点上使用同一RHF/STO-3G哈密顿量和`FUL→PDSI→DSI2→FUD→G`状态路径。

## 用途

本记录把P04、P05和P06三个已冻结范围化科学发布映射为P07命题级证据矩阵，用于判断简单“共轭稳定化—位阻去稳定化”二项叙事能否覆盖现有source-defined结果。

## 输入

- P04：33条Target C记录，11个有效source-proxy点；
- P05：原冻结0°/17°账本及后续同体系七角度增强；
- P06：6条Target B记录，0°/17°。

生成器保存三个输入文件的路径、SHA-256、记录数和各自专用验证器判定。任何输入变化都会使P07验证失败。

## 输出语义

旧`result.json`保留P04–P06命题综合；新增`same-hamiltonian-audit-result.json`记录独立路径审计。当前核心判定为：

`P07_CONSISTENT_WITH_INDEPENDENT_SAME_HAMILTONIAN_PATH_AUDIT`

同哈密顿量审计表明，未经桥接定义的π–π、π–σ和`E_PDSI-E_FUL` σ子项相加，在0°/17°分别残留`0.335760104092/0.333815958695 Eh`；加入`E_DSI2-E_PDSI`桥接项，或将σ项改为路径完整的`E_DSI2-E_FUL`后，均严格闭合。因此各分量必须在明确状态路径下分别定义和计算，不能仅凭传统二项叙事预判。

## 禁止用途

- 禁止把A/B/C的Hartree值相加为统一总能量；
- 禁止解释为完整扭转PES、扭矩或优化几何的因果证明；
- 禁止升级为所有分子的普遍稳定化/去稳定化定律；
- 禁止作为MACE/PySR生产训练标签或工业级泛化证据。
