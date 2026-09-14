# AI4OrgChem

[![Validation](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml/badge.svg)](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/CCcolab/AI4OrgChem)](LICENSE)
[![Evidence](https://img.shields.io/badge/evidence-P01--P14%20internally%20checked-2ea44f)](evidence/P01-P14/README_zh-CN.md)
[![WSL2](https://img.shields.io/badge/WSL2-Ubuntu%2024.04%20verified-0078D4)](reproducibility/wsl/README.md)
[![AI辅助](https://img.shields.io/badge/AI%20assistance-OpenAI%20Codex%20GPT--5.6-6f42c1)](AUTHORS.md)

[English](README.md)

AI4OrgChem是一个面向有机结构基础理论独立计算重构与证据评估的 **AI for Science（AI4S）Agent**。项目以虞忠衡教授的学术专著《Questioning Fundamental Principles of Organic Chemistry》（2024）提出的反传统命题为科学起点，完全不使用原著程序代码进行独立实现。

> **AI辅助研究与工程支持：** **OpenAI Codex（GPT-5.6）**。项目作者身份、科学决策、结果解释和发布责任均由Xiao Chen承担；OpenAI不作为项目作者、科学认证机构、同行评审方或机构背书方。

相关论文稿尚未经过同行评审。逐项判定、限定条件与勘误见[总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)及其所链接的命题记录。

## 项目背景与目标

共轭稳定化、共轭促平面化、位阻去稳定化和芳香稳定化是有机化学中非常有用的经验启发式。问题在于，经验趋势不能自动获得无条件因果定律的地位。AI4OrgChem将原著十四项主要命题转化为可证伪计算任务，冻结分子体系、状态定义、符号约定、机器结果和适用边界。

项目关注的是：独立计算与其他可追溯证据在明确的分子和方法范围内能支持命题到什么程度，哪些问题仍缺少充分证据。

## 独立研究方法

- 先定义分子、几何、电子态、哈密顿量、比较量、符号约定和判定边界，再评估命题。
- 对适用命题独立实现轨道局域化、条件电子结构计算、几何或能量扫描及能量分解；不使用原著程序代码。
- 区分量子化学计算、已发表数值复分析、图论检查和文献旁证；命题级评估不等于十四项均完成同等级量化复算。
- AI4S Agent辅助协议管理、证据追踪、有界分子学习、主动采样、符号检验和来源可查的解释；模型预测不替代电子结构结果，也不决定科学符号。

## 科学论证结果

项目已为十四项命题建立协议、处理后结果、数据卡和限定范围的报告，并公开可检查这些记录的软件与验证入口。各项结论及其限制详见[命题证据导航](evidence/P01-P14/README_zh-CN.md)和[总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)。

代表性冻结结果如下：

| 结果 | 数值或分类 |
|---|---:|
| 技术有效LFMO π–π端点 | 11/11为去稳定化方向 |
| GL定义的丁二烯共轭能 | +1.575676 kcal/mol |
| 环丁二烯ADE | +53.822467 kcal/mol |
| 苯ESE | -37.412764 kcal/mol（原著 -36.3；绝对差1.112764，约3.07%） |
| 应变芳香C12H6端点 | +67.086899 kcal/mol固定几何原著层级锚点；+67.679719 kcal/mol合格生产优化（`dΔr=0.172204 Å`） |

这些结果支持一个有边界的方法论结论：若干教科书启发式不能自动成为普遍充分的机制解释。项目不据此宣称传统有机化学整体错误，不建立“共轭必然去稳定化”的反向普遍定律，也不把本项目描述为对原著的机构认证。

十四项属于分层、可审计证据链，并非十四次同等级量子化学复现；独立QM、source-aligned/source-proxy重构、发表值复分析和图论/文献旁证的证据身份分别保留。

其他成果包括同哈密顿量状态路径审计、逐状态平面复算，以及对应变芳香端点的证据资格检查。具体结论与被后续结果取代的旧记录均保留在各命题报告中。

详见[P01–P14总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)和[中文命题证据导航](evidence/P01-P14/README_zh-CN.md)。

量子化学、计算化学或有机结构理论领域的读者可直接阅读[AI4S快速复算与证据核验指南](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md)：10分钟理解总体论证，30分钟核验任意一项命题，无需先阅读代码。

## 社区复核

项目欢迎独立复现、可证伪检验和有边界的科学异议。请使用结构化Issue表单提交[独立复现报告](https://github.com/CCcolab/AI4OrgChem/issues/new?template=independent-reproduction.yml)、[科学异议](https://github.com/CCcolab/AI4OrgChem/issues/new?template=scientific-disagreement.yml)、[文档修正](https://github.com/CCcolab/AI4OrgChem/issues/new?template=documentation-correction.yml)或[新分子测试建议](https://github.com/CCcolab/AI4OrgChem/issues/new?template=new-molecular-test.yml)。

## AI4S Agent工程成果

已经完成的有界工程线把冻结科学证据连接到机器可读数据、等变模型、主动学习回流、符号发现和只读证据Agent。

- 有界数据集：17个几何、3个分子家族、5个能量目标；
- π–π家族留出宏平均RMSE：MACE为108.0 meV/atom，NequIP为108.2 meV/atom；
- 主动学习：候选采样成功，真实标签回流后的模型效果有好有坏；
- PySR：π–π有界盲测通过，π–σ盲测失败；
- 证据Agent：只允许检索冻结证据，必须显示来源和适用范围。

当前数据规模不足以支持工业级或任意分子泛化。详见[Agent能力与结果](ai4s-agent/CAPABILITIES_AND_RESULTS_zh-CN.md)、[机器评估摘要](ai4s-agent/EVALUATION_SUMMARY.json)和[限制说明](ai4s-agent/LIMITATIONS_zh-CN.md)。

## 仓库导航

| 栏目 | 内容 |
|---|---|
| [快速复算与证据核验指南](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md) | 面向科学读者的AI4S快速复算与证据核验路线 |
| [项目背景](project/README.md) | 项目背景、研究项、研究价值、成果和命题总表 |
| [P01–P14证据](evidence/P01-P14/README_zh-CN.md) | 冻结数据卡、协议、处理后结果和范围化报告 |
| [发表材料](manuscripts/README.md) | 证据矩阵和双语发布定位 |
| [AI4S Agent](ai4s-agent/README.md) | Agent架构、能力、评估、证据治理和限制 |
| [公开软件](software/README.md) | LFMO/条件SCF公开核心实现和69项测试 |
| [典型程序复算入口](reproducibility/TYPICAL_PROGRAMS_zh-CN.md) | 按计算难度选择证据核验、条件SCF测试和可下载QM复算，并查看逐步计算说明 |
| [复现说明](reproducibility/README.md) | 完整复现说明、运行环境和WSL 2平台边界 |
| [图表](figures/README.md) | 项目自行生成的总览图 |
| [科学增强证据](science-v0.2/README.md) | 自包含配置、精选结果、判定、报告、测试与哈希 |
| [科学闭合证据](science-v0.3/README.md) | 七工作包扩展及其独立证据边界 |
| [文件清单](manifests/FILE_INVENTORY.md) | 文件清单和SHA-256清单 |

## 阅读与复核

可从[快速证据核验指南](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md)或[典型程序复算入口](reproducibility/TYPICAL_PROGRAMS_zh-CN.md)开始。[详细计算说明](reproducibility/DETAILED_COMPUTATION_GUIDE_zh-CN.md)、[中文运行手册](reproducibility/RUNBOOK_zh-CN.md)和[平台矩阵](reproducibility/PLATFORM_MATRIX_zh-CN.md)列明命令、硬件要求，以及证据检查与高成本量化复算的区别。

## 复现与证据边界

- 不发布原著、扫描件、出版商文件、全文提取或历史程序代码；
- 部分历史Cartesian坐标和程序未公开，相应结果明确标记为source-proxy，不冒充历史身份复现；
- 不同状态合同的Target禁止跨协议直接求和；
- AI模型输出属于工程证据，不是新的量子化学标签，也不替代科学命题论证；
- 模型、私有运行目录、缓存、API凭据和受版权保护材料不进入公共仓库。

## 证据矩阵与发布定位

- [十四项总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)
- [中文发布定位](manuscripts/PUBLICATION_POSITIONING_zh-CN.md)

## 许可证

本项目自行形成的软件和文档采用[Apache License 2.0](LICENSE)。第三方边界见[NOTICE](NOTICE)。该许可证不重新授权原著或其他第三方材料。

## 引用

本项目唯一作者为 **Xiao Chen**。联系方式：[chenxiao0101@gmail.com](mailto:chenxiao0101@gmail.com)。本项目使用 **OpenAI Codex（GPT-5.6）** 提供AI辅助研究与工程支持。作者身份、CRediT贡献、AI辅助披露和利益冲突声明见[作者声明](AUTHORS.md)；机器可读引用信息见[引用文件](CITATION.cff)。因未提供机构和ORCID，目前不填写相关信息。
