# 运行平台矩阵

## 权威环境声明

AI4OrgChem的科学计算与AI训练结果是在 **WSL 2 / Ubuntu 24.04** 中形成并验证的。WSL 2不是项目概念上的必需条件，但它是本项目已获得证据的权威运行平台；未验证的平台不能被表述为等价复现。

| 内容 | 权威/推荐平台 | 原生Windows状态 | GitHub首版承诺 |
|---|---|---|---|
| Markdown、JSON/JSONL证据阅读 | 任意平台 | 支持 | 完整支持 |
| `validate_public_evidence.py` | Python 3.12，WSL/Linux优先 | 可运行 | 验证冻结结果完整性 |
| NumPy LFMO子空间与掩码单元测试 | WSL 2 / Linux | 可能运行，但非权威环境 | 提供代码与测试 |
| PySCF条件SCF及量子化学主线 | WSL 2 / Ubuntu 24.04 | 未认证为等价环境 | 提供核心实现；不承诺首版重算全部昂贵任务 |
| MACE GPU训练 | WSL 2 + CUDA 12.6兼容PyTorch | 未在原生Windows认证 | 仅披露冻结评估摘要，不发布缓存和模型 |
| NequIP GPU对照 | WSL 2 + 独立环境 + CUDA | 未在原生Windows认证 | 仅披露冻结评估摘要 |
| PySR符号搜索 | WSL 2 + Julia/Python运行时 | 未在原生Windows认证 | 仅披露冻结盲测结论 |
| 本地只读WebUI/证据Agent | 本地浏览器与受控后端 | 属于本地交付，不是GitHub首版运行前提 | 首版只发布架构、能力、结果和限制说明 |

## 环境隔离

- 不覆盖或升级用户现有WSL 2环境；
- 公开CPU复核环境使用`ai4orgchem-public`，与项目历史运行环境区分；
- MACE和NequIP因`e3nn`依赖不同，在历史验证中使用两个隔离环境；
- GitHub首版`environment.yml`不声称复刻这两个GPU训练环境；完整GPU锁定文件应与模型/数据归档在后续版本单独发布。
