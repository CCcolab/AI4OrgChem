# AI4OrgChem

[![Release](https://img.shields.io/github/v/release/CCcolab/AI4OrgChem?display_name=tag&sort=semver)](https://github.com/CCcolab/AI4OrgChem/releases/latest)
[![Validation](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml/badge.svg)](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/CCcolab/AI4OrgChem)](LICENSE)
[![Evidence](https://img.shields.io/badge/evidence-P01--P14%20validated-2ea44f)](evidence/P01-P14/README_zh-CN.md)
[![WSL2](https://img.shields.io/badge/WSL2-Ubuntu%2024.04%20verified-0078D4)](reproducibility/wsl/README.md)
[![AI辅助](https://img.shields.io/badge/AI%20assistance-OpenAI%20Codex%20GPT--5.6-6f42c1)](AUTHORS.md)

[English](README.md)

AI4OrgChem是一个面向有机结构基础理论独立计算重构与证据评估的 **AI for Science（AI4S）Agent**。项目以虞忠衡教授的学术专著《Questioning Fundamental Principles of Organic Chemistry》（2024）提出的反传统命题为科学起点，完全不使用原著程序代码进行独立实现。

> **AI辅助研究与工程支持：** **OpenAI Codex（GPT-5.6）**。项目作者身份、科学决策、结果解释和发布责任均由Xiao Chen承担；OpenAI不作为项目作者、科学认证机构、同行评审方或机构背书方。

> **发布状态：** 安全加固精选版本 `v0.1.2`。相关论文稿尚未经过同行评审。

## 项目背景与目标

共轭稳定化、共轭促平面化、位阻去稳定化和芳香稳定化是有机化学中非常有用的经验启发式。问题在于，经验趋势不能自动获得无条件因果定律的地位。AI4OrgChem将原著十四项主要命题转化为可证伪计算任务，冻结分子体系、状态定义、符号约定、机器结果和适用边界。

项目判断独立重构的量子化学证据在受测域内是支持、反对还是部分支持每项命题。AI用于协议管理、证据追踪、有界分子学习、主动采样、符号检验和解释，不负责指定科学符号，也不替代电子结构计算。

## 科学论证结果

十四项命题均形成确定性分类：

- **12项一致或范围化一致**；
- **2项部分一致**：P11保留取代苯诱导分量异号，P12保留轮烯精确尺寸起点的跨估计量差异；
- **整体不一致0项，未知0项**。

代表性冻结结果如下：

| 结果 | 数值或分类 |
|---|---:|
| 技术有效LFMO π–π端点 | 11/11为去稳定化方向 |
| GL定义的丁二烯共轭能 | +1.575676 kcal/mol |
| 环丁二烯ADE | +53.822467 kcal/mol |
| 苯ESE | -37.412764 kcal/mol |
| 应变芳香C12H6端点 | +67.086899 kcal/mol |

这些结果支持一个有边界的方法论结论：若干教科书启发式不能自动成为普遍充分的机制解释。项目不据此宣称传统有机化学整体错误，不建立“共轭必然去稳定化”的反向普遍定律，也不把本项目描述为对原著的机构认证。

详见[P01–P14总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)和[中文命题证据导航](evidence/P01-P14/README_zh-CN.md)。

如果您是量子化学领域专家，但不熟悉GitHub、AI或软件工程，可直接阅读[面向量子化学专家的快速审阅指南](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md)：10分钟理解总体论证，30分钟核查任意一项命题，无需先阅读代码。

## 社区复核

项目欢迎独立复现、可证伪检验和有边界的科学异议。请使用结构化Issue表单提交[独立复现报告](https://github.com/CCcolab/AI4OrgChem/issues/new?template=independent-reproduction.yml)、[科学异议](https://github.com/CCcolab/AI4OrgChem/issues/new?template=scientific-disagreement.yml)、[文档修正](https://github.com/CCcolab/AI4OrgChem/issues/new?template=documentation-correction.yml)或[新分子测试建议](https://github.com/CCcolab/AI4OrgChem/issues/new?template=new-molecular-test.yml)。一般性问题和解释讨论请使用[GitHub Discussions](https://github.com/CCcolab/AI4OrgChem/discussions)。

## AI4S Agent工程成果

已经完成的有界工程线把冻结科学证据连接到机器可读数据、等变模型、主动学习回流、符号发现和只读证据Agent。

- 有界数据集：17个几何、3个分子家族、5个能量目标；
- π–π家族留出宏平均RMSE：MACE为108.0 meV/atom，NequIP为108.2 meV/atom；
- 主动学习：候选采样成功，真实标签回流后的模型效果有好有坏；
- PySR：π–π有界盲测通过，π–σ盲测失败；
- 证据Agent：只允许检索冻结证据，必须显示来源和适用范围。

当前数据规模不足以支持工业级或任意分子泛化。详见[Agent能力与结果](ai4s-agent/CAPABILITIES_AND_RESULTS_zh-CN.md)、[机器评估摘要](ai4s-agent/EVALUATION_SUMMARY.json)和[限制说明](ai4s-agent/LIMITATIONS_zh-CN.md)。

## 仓库导航

| 路径 | 内容 |
|---|---|
| [`REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md`](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md) | 非计算机/AI专业量子化学专家快速审阅路线 |
| [`project/`](project/README.md) | 项目背景、研究项、研究价值、成果和命题总表 |
| [`evidence/P01-P14/`](evidence/P01-P14/README_zh-CN.md) | 冻结数据卡、协议、处理后结果和范围化报告 |
| [`manuscripts/`](manuscripts/README.md) | 中英文论文、证据矩阵和发布定位 |
| [`ai4s-agent/`](ai4s-agent/README.md) | Agent架构、能力、评估、证据治理和限制 |
| [`software/`](software/README.md) | LFMO/条件SCF公开核心实现和64项测试 |
| [`reproducibility/`](reproducibility/README.md) | 复现说明和WSL 2平台边界 |
| [`figures/`](figures/README.md) | 项目自行生成的总览图 |
| [`manifests/`](manifests/FILE_INVENTORY.md) | 文件清单和SHA-256清单 |

## 快速验证

不重新执行昂贵量子化学计算，直接检查P01–P14处理后证据与冻结判定：

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```

预期输出包含`"status": "PASS"`、`"propositions_checked": 14`和`"propositions_navigated": 14`。

安装并运行公开核心测试：

```bash
cd software
python -m pip install -e ".[science,test]"
python -m pytest -p no:cacheprovider
```

权威科学运行平台为 **WSL 2 / Ubuntu 24.04**。原生Windows只支持有限证据复核，不被声明为PySCF量化主线、MACE/NequIP CUDA训练或PySR运行结果的等价环境。详见[中文平台矩阵](reproducibility/PLATFORM_MATRIX_zh-CN.md)、[中文运行手册](reproducibility/RUNBOOK_zh-CN.md)和[可移植WSL入口](reproducibility/wsl/README.md)。

## 复现与证据边界

- 不发布原著、扫描件、出版商文件、全文提取或历史程序代码；
- 部分历史Cartesian坐标和程序未公开，相应结果明确标记为source-proxy，不冒充历史身份复现；
- 不同状态合同的Target禁止跨协议直接求和；
- AI模型输出属于工程证据，不是新的量子化学标签，也不替代科学命题论证；
- 模型、私有运行目录、缓存、API凭据和受版权保护材料不进入本发布版本。

## 论文稿件

- [英文论文](manuscripts/MANUSCRIPT_EN.md)
- [中文论文](manuscripts/MANUSCRIPT_zh-CN.md)
- [中文发布定位](manuscripts/PUBLICATION_POSITIONING_zh-CN.md)

## 许可证

本项目自行形成的软件和文档采用[Apache License 2.0](LICENSE)。第三方边界见[NOTICE](NOTICE)。该许可证不重新授权原著或其他第三方材料。

## 引用

本项目唯一作者为 **Xiao Chen**。联系方式：[chenxiao0101@gmail.com](mailto:chenxiao0101@gmail.com)。本项目使用 **OpenAI Codex（GPT-5.6）** 提供AI辅助研究与工程支持。作者身份、CRediT贡献、AI辅助披露和利益冲突声明见[`AUTHORS.md`](AUTHORS.md)；机器可读引用信息见[`CITATION.cff`](CITATION.cff)。因未提供机构和ORCID，本版本不填写相关信息。
