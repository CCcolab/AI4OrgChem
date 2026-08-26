# P01–P14证据导航

[English](README.md)

本导航把每项范围化科学判定连接到冻结数据卡、协议、机器结果和报告。“一致”只表示在声明受测域内与原著相应命题一致，不等于历史身份复现、普遍定律或机构认证。

## 分类汇总

- 一致或范围化一致：12项；
- 部分一致：2项，即P11和P12；
- 整体不一致：0项；
- 未知：0项。

| ID | 受测命题 | 项目判定 | 关键证据与边界 | 文件 |
|---|---|---|---|---|
| P01 | 必须区分分子轨道表达与电子密度离域。 | **一致** | canonical/localized占据空间变换保持同一状态密度和RHF能量；限于单参考操作定义。 | [数据卡](P01/data-card.md) · [协议](P01/protocol.md) · [机器结果](P01/result.json) · [报告](P01/report.md) |
| P02 | 共轭可以伴随而不是阻止分子扭曲。 | **一致** | 公开结构值和同系UV趋势支持范围化方向；未重新精修原始CIF。 | [数据卡](P02/data-card.md) · [协议](P02/protocol.md) · [机器结果](P02/result.json) · [报告](P02/report.md) |
| P03 | 在受测parent NBA路径上，电子能可促进扭曲，核排斥变化方向相反。 | **一致** | 单一source-aligned parent NBA弛豫定扭转PES及电子能/核排斥分离；不外推跨分子定律。 | [数据卡](P03/data-card.md) · [协议](P03/protocol.md) · [机器结果](P03/result.json) · [报告](P03/report.md) |
| P04 | LFMO定义下π–π端点可以为去稳定化。 | **一致** | 11个技术有效source-proxy端点全部为去稳定化方向；不表示任意共轭分子必为该符号。 | [数据卡](P04/data-card.md) · [协议](P04/protocol.md) · [机器结果](P04/result.jsonl) · [报告](P04/report.md) |
| P05 | π–σ源端点可以为去稳定化。 | **范围化一致** | Table 5-15 source-proxy的17°端点为正；0°点在容差内不能定号。 | [数据卡](P05/data-card.md) · [协议](P05/protocol.md) · [机器结果](P05/result.jsonl) · [报告](P05/report.md) |
| P06 | 非键σ–σ必须按明确条件态分析，不能自动等同经典位阻能。 | **一致** | 冻结Table 5-19的两个source-proxy端点在PDSI/FUL状态对下均为去稳定化。 | [数据卡](P06/data-card.md) · [协议](P06/protocol.md) · [机器结果](P06/result.jsonl) · [报告](P06/report.md) |
| P07 | “共轭稳定化—位阻去稳定化”二项叙事不足以解释受测机制。 | **范围化一致** | 综合论证必须同时核查π–π、π–σ、σ–σ及响应；不同状态合同的能量禁止求和。 | [数据卡](P07/data-card.md) · [协议](P07/protocol.md) · [机器结果](P07/result.json) · [报告](P07/report.md) |
| P08 | GL定义的丁二烯共轭能可以为正，氢化热参照不能确定唯一符号。 | **一致** | 冻结GL结果为 **+1.575676 kcal/mol**；属于独立实现，不冒充历史程序身份复现。 | [数据卡](P08/data-card.md) · [协议](P08/protocol.md) · [机器结果](P08/result.json) · [报告](P08/report.md) |
| P09 | 芳香/反芳香能可以由理论局域/虚拟参照构造。 | **一致** | 环丁二烯ADE为 **+53.822467 kcal/mol**，苯ESE为 **-37.412764 kcal/mol**。 | [数据卡](P09/data-card.md) · [协议](P09/protocol.md) · [机器结果](P09/result.json) · [报告](P09/report.md) |
| P10 | 在受测苯键长交替坐标上，核排斥变化是主要能量项。 | **一致** | 电子能与核排斥贡献方向相反；不把核排斥描述为脱离电子结构的孤立原因。 | [数据卡](P10/data-card.md) · [协议](P10/protocol.md) · [机器结果](P10/result.json) · [报告](P10/report.md) |
| P11 | 呋喃需用LDE处理；取代苯应分离共轭与诱导分量。 | **部分一致** | P11-A呋喃LDE一致。P11-B共轭项 **+1.180928**，与原著 **+1.2 kcal/mol**一致；但两种诱导诊断均为负（**-0.335714**、**-0.580151**），原著为 **+0.49**。完整历史氰基苯Cartesian坐标未公开。 | 呋喃：[数据卡](P11/furan-data-card.md) · [协议](P11/furan-protocol.md) · [结果](P11/furan-result.json) · [报告](P11/furan-report.md)。取代基：[数据卡](P11/substituent-data-card.md) · [协议](P11/substituent-protocol.md) · [结果](P11/substituent-result.json) · [报告](P11/substituent-report.md) |
| P12 | 大轮烯趋近多烯能量行为，但精确尺寸边界依赖估计量。 | **部分一致** | 大环定性趋势一致；原著账本起点为 **N=16/18**，独立ASE趋势为 **N>30**。因两者估计量不同，保留为起点差异，而不称同估计量直接反证。 | [数据卡](P12/data-card.md) · [协议](P12/protocol.md) · [机器结果](P12/result.json) · [报告](P12/report.md) |
| P13 | 多环苯系需要受测GL/位置/能量规则层级，不能只依赖简单局域计数。 | **一致** | 独立图枚举和公开能量账本支持范围化规则层级；未重跑完整历史优化面板。 | [数据卡](P13/data-card.md) · [协议](P13/protocol.md) · [机器结果](P13/result.json) · [报告](P13/report.md) |
| P14 | π相互作用可参与应变芳香体系的结构扭曲。 | **一致** | 冻结C12H6 source-proxy端点为 **+67.086899 kcal/mol**；不外推完整应变芳香面板。 | [数据卡](P14/data-card.md) · [协议](P14/protocol.md) · [机器结果](P14/result.json) · [报告](P14/report.md) |

## P11为何只能判“部分一致”

P11包含两个子命题。呋喃LDE的方向和幅度通过；氰基苯共轭项也与原著接近。但诱导项的符号在同实现苯锚点和公开苯锚点两种诊断下都为负，而原著为正，因此不能把P11整体写成完全一致。由于完整历史Cartesian坐标缺失，本项目也不把source-proxy下的异号升级为对原著历史坐标计算的直接反驳。

## P12为何只能判“部分一致”

原著六点账本支持轮烯随尺寸增加趋近多烯/能量非芳香行为，独立研究也支持大环极限的定性趋势。但原著CESE/ΔEA语义的起点是N=16/18，独立ASE估计的边界为N>30。二者测量对象不同，所以“最终趋近”的方向一致，而“从哪个尺寸开始”的数值不能视为独立复现。

## 自动验证

在仓库根目录运行：

```bash
python software/scripts/validate_public_evidence.py
```

验证器必须返回`status: PASS`并检查14项机器结果。跨命题总矩阵见[`manuscripts/P01-P14_evidence_matrix_zh-CN.md`](../../manuscripts/P01-P14_evidence_matrix_zh-CN.md)。

## 证据边界

- 公开包包含处理后证据和冻结结论，不包含受版权保护的原始材料或私有运行目录；
- 冻结结果中的`production_label=false`记录该证据的科学/机器学习边界，不得静默改写；
- source-proxy、source-aligned重构和历史身份复现是不同证据等级；
- AI预测和符号候选不能修改P01–P14科学判定。
