# AI4OrgChem 详细计算说明（WSL 2）

本页承接项目首页原有的逐项计算入口、运行平台、资源约束与复核命令；从仓库根目录执行命令。

### 为什么本项目把WSL 2作为权威计算平台

WSL 2不是这些量子化学公式成立的数学前提，但它是本项目**实际形成并验证科学结果的权威运行平台**。因此，“必须在WSL 2算”的准确含义是：若要声称与本项目运行环境等价，必须在已经验证的WSL 2 / Ubuntu 24.04软件栈中复核；原生Windows只用于阅读、轻量检查和发布整理，不被认证为PySCF科学主线、MACE/NequIP CUDA训练或PySR搜索的等价环境。

选择该平台的工程原因包括：Linux优先的PySCF与科学Python依赖；WSL GPU透传下已经跑通的CUDA/PyTorch链；MACE与NequIP不兼容`e3nn`版本的环境隔离；POSIX Shell入口；以及统一的线程、内存、进程和可写scratch边界。WSL环境是“经验证的平台合同”，不是把Windows目录整体复制进Linux，也不允许覆盖用户已有环境。

### 硬件与软件栈

| 层级 | 本项目已验证配置 | 使用边界 |
|---|---|---|
| 主机CPU | Intel Core Ultra 9 185H；16物理核、22逻辑处理器 | 默认8线程；重新基准测试前不超过16线程；中高内存QM任务同时只跑1个 |
| WSL内存 | 可见约15 GiB，swap 4 GiB | 可用内存低于4 GiB停止新作业；swap不作为常规OOM方案 |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU，8188 MiB VRAM，compute capability 8.9 | 用于第五期MACE/NequIP；量子化学定判不以GPU模型输出替代 |
| 操作系统 | WSL 2 / Ubuntu 24.04 | 本项目科学与GPU结果的权威平台 |
| 环境管理 | micromamba；Python 3.12 | 公开复核环境为`ai4orgchem-public`；历史工程环境彼此隔离且不得强制更新 |
| 量子化学 | PySCF 2.x；RHF、B3LYP及B3LYPG/6-31G(d)、RHF/STO-3G等冻结协议 | 方法、基组、几何和状态合同以每项protocol为准，不跨协议混算 |
| 分析与数据 | NumPy、SciPy、PyYAML、RDKit、JSON/JSONL | 子空间、能量组装、统计、图论、分子式和证据账本 |
| AI工程 | PyTorch 2.10.0+cu126、CUDA 12.6、MACE 0.3.16、NequIP 0.19.0、PySR/Julia | 仅支持有界工程结论；MACE与NequIP使用隔离环境 |

### 在WSL 2里完成的计算任务

本项目在WSL 2中执行了五类任务：①公开结构/光谱数据回归和数值账本重算；②约束或弛豫PES、几何优化与电子能/核排斥分解；③LFMO子空间、条件SCF、DSI/FUD/FUL/PDSI/GL/PLG状态及独立能量组装；④芳香/反芳香虚拟参考、LDE/ESE/VDE/ADE/CESE和图论规则检验；⑤第五期的MACE/NequIP训练、真实QM标签回流和PySR盲测。前四类形成P01–P14科学证据；第五类只检验AI4S工程可行性，不反向改变十四项判定。

### 十四项 × WSL 2定判入口

并非十四项都是昂贵量子化学任务。P02主要是公开表值统计复核，P12是源账本与独立趋势比较，P13包含图论和分子式校验；表中明确列出每项在WSL 2上实际执行的任务。

| 项号 | 在WSL 2上算什么 | 定判入口模块 | 主方法 |
|---|---|---|---|
| P01 | 同占据空间轨道变换、AO密度与RHF能量不变性、LFMO状态比较 | [protocol](../evidence/P01-P14/P01/protocol.md) · [result](../evidence/P01-P14/P01/result.json) | canonical/Boys/Pipek–Mezey、LFMO子空间、DSI-3/FUD |
| P02 | 公开X射线/UV表值、同系线回归、键长和扭转角方向复核 | [protocol](../evidence/P01-P14/P02/protocol.md) · [result](../evidence/P01-P14/P02/result.json) | 单一已发表晶体对的结构—光谱关联；不作因果断言 |
| P03 | parent NBA弛豫PES及电子能、核排斥能、总能、曲率和扭矩 | [protocol](../evidence/P01-P14/P03/protocol.md) · [result](../evidence/P01-P14/P03/result.json) | 冻结坐标电子—核账本及抵消；不作第一原因断言 |
| P04 | 三个分子家族、多个角度的DSI-3/FUD π–π端点和响应诊断 | [protocol](../evidence/P01-P14/P04/protocol.md) · [result](../evidence/P01-P14/P04/result.jsonl) | PySCF RHF/6-31G(d)、LFMO、11点source-proxy面板 |
| P05 | 0°–45°七角度G/FUD π–σ端点及直接作用—轨道响应 | [protocol](../evidence/P01-P14/P05/protocol.md) · [result](../evidence/P01-P14/P05/seven-angle-result.json) | Target A、RHF/6-31G(d)、原著分量公式；六个非零角度均为正 |
| P06 | 0°/17° FUL/PDSI非键σ–σ条件态能量差 | [protocol](../evidence/P01-P14/P06/protocol.md) · [result](../evidence/P01-P14/P06/result.jsonl) | Target B、RHF/STO-3G、独立能量组装 |
| P07 | 同哈密顿量五状态路径审计＋P04/P05/P06命题综合 | [protocol](../evidence/P01-P14/P07/protocol.md) · [audit](../evidence/P01-P14/P07/same-hamiltonian-audit-result.json) · [synthesis](../evidence/P01-P14/P07/result.json) | 状态特异LFMO；显式桥接/路径完整σ定义；禁止跨协议求和 |
| P08 | 丁二烯G/GL平面优化、共轭能、中央键差和三种氢化热参照 | [protocol](../evidence/P01-P14/P08/protocol.md) · [result](../evidence/P01-P14/P08/result.json) | GL(2014) source-aligned、B3LYPG/6-31G(d) |
| P09 | 环丁二烯VDE/ADE与苯ESE的虚拟参考和独立能量组装 | [protocol](../evidence/P01-P14/P09/protocol.md) · [result](../evidence/P01-P14/P09/result.json) | G/DSI/GL、G/GL/GE-1/VR、B3LYP/6-31G(d) |
| P10 | 苯键长交替五点扫描、电子能/核排斥能/总能及曲率 | [protocol](../evidence/P01-P14/P10/protocol.md) · [result](../evidence/P01-P14/P10/result.json) | B3LYPG/6-31G(d)、独立核间库仑和 |
| P11 | 呋喃LDE；氰基苯/苯13态全平面逐态受限优化与共轭/诱导贡献 | [furan protocol](../evidence/P01-P14/P11/furan-protocol.md) · [furan result](../evidence/P01-P14/P11/furan-result.json) · [substituent protocol](../evidence/P01-P14/P11/substituent-protocol.md) · [substituent result](../evidence/P01-P14/P11/substituent-result.json) | source-2007 LDE、Fock/overlap条件SCF、state-specific planar optimization、ESE/CE/IE差分 |
| P12 | 六点轮烯源表算术与账本内尺寸变化；不同估计量的ASE趋势仅作旁证 | [protocol](../evidence/P01-P14/P12/protocol.md) · [result](../evidence/P01-P14/P12/result.json) · [corrigendum](../P12_CORRIGENDUM.md) | VDE/ESE/CESE、相对局域增量；不作跨估计量同口径阈值判定 |
| P13 | Kekulé候选枚举、GL规则优先级、RDKit分子式和PBH账本 | [protocol](../evidence/P01-P14/P13/protocol.md) · [result](../evidence/P01-P14/P13/result.json) | 图论完美匹配、RDKit、公开数值账本 |
| P14 | C12H6 PLG条件SCF、固定几何端点、B3LYPG/6-31G(d)五参数生产优化及证据资格门禁 | [protocol](../evidence/P01-P14/P14/protocol.md) · [result](../evidence/P01-P14/P14/result.json) | **一致**；G/PLG梯度、终止、边界、SCF、电子数及结构/能量容差全部通过 |

统一机器定判入口为[`validate_public_evidence.py`](../software/scripts/validate_public_evidence.py)；双语导航和P11/P12差异由[`validate_evidence_navigation.py`](../software/scripts/validate_evidence_navigation.py)复核。定判入口读取冻结结果，不重新伪装成一次完整历史计算。

### 单次作业的数据流（WSL 2内）

```text
冻结命题与protocol
  → 环境/线程/内存预检
  → 分子、坐标、角度或公开数值账本
  → SCF/条件SCF/几何优化/PES/图论或统计任务
  → LFMO π/σ分类与状态构造（适用时）
  → 独立能量组装、收敛与物理诊断
  → processed JSON/JSONL冻结结果
  → 命题验证器与范围化判定
  → 数据卡、报告、文件清单和SHA-256快照
```

非QM命题跳过SCF步骤，但仍执行相同的协议冻结、来源追踪、机器结果和验证门禁。

### 计算纪律（WSL 2同样强制）

- 先冻结分子、Cartesian几何或source-proxy、电子态、方法、基组、符号和完成规则，再运行；
- 同一比较必须保持同几何、同基组和同状态合同；不同Target或不同估计量不得直接相加；
- SCF收敛、电子数、自旋、占据、LFMO连续分类、内存和能量闭合失败必须保留为失败，不得静默删点；
- 历史坐标或程序不完整时必须标记`source-proxy`，不得宣称原厂代码或历史坐标身份复现；
- 默认8 CPU线程；中高内存QM任务串行；低内存门槛触发停止，不用swap掩盖OOM；
- 不覆盖现有micromamba环境；MACE与NequIP运行时分离；公开复核环境只在不存在时显式创建；
- AI预测、PySR公式和LLM解释不能生成或改写科学生产标签；P01–P14只由冻结量子化学/数值证据定判；
- 不使用原著程序代码，不把受版权保护全文、API密钥、本机路径、缓存或模型权重写入发布快照。

### 本目录内容（归档结构）

```text
AI4OrgChem/
├─ project/                 # 背景、研究项、价值、成果与十四项总表
├─ evidence/P01-P14/        # 每项data-card、protocol、result、report
├─ software/                # LFMO/条件SCF核心、69项测试、验证与刷新入口
├─ reproducibility/         # 双语运行手册、平台矩阵、环境与WSL入口
├─ configs/qm/              # 可公开的冻结量化配置
├─ manuscripts/             # Evidence matrix and publication positioning
├─ ai4s-agent/              # AI工程能力、评估、治理与限制
├─ figures/                 # 项目自行生成的图
├─ manifests/               # 实质文件清单与SHA-256快照
└─ .github/workflows/       # 不调用Secret/LLM/昂贵QM的公开CI
```

原始量化输出、scratch、历史开发日志、模型权重、私有运行目录和原著文件不属于本精选归档。

### 在WSL 2中复现（操作摘要）

```powershell
wsl -d Ubuntu-24.04
```

进入仓库根目录后：

```bash
micromamba env list
# 仅当 ai4orgchem-public 不存在时：
micromamba create -f reproducibility/environment.yml
source reproducibility/wsl/activate-ai4orgchem-public.sh

bash reproducibility/wsl/ai4orgchem-verify
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py

cd software
python -m pip install -e ".[science,test]"
python -m pytest -p no:cacheprovider
```

上述步骤复核冻结证据和公开核心软件，不承诺从精选包重跑所有历史昂贵作业。完整说明见[中文运行手册](../reproducibility/RUNBOOK_zh-CN.md)。

### 刷新本快照

结果文件不能手工改值。只有在协议授权的源数据、代码或文档发生变更并完成复算后，维护者才可在仓库根目录执行：

```bash
python software/scripts/refresh_release_snapshot.py
python software/scripts/validate_release_package.py
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
```

刷新只重建文件清单和SHA-256快照，不生成量子化学结论；随后必须重新运行69项测试、洁净克隆和Ubuntu入口验证，并创建新提交/不可变版本标签。外部复核者通常只需验证快照，无需刷新。

### 相关文档

- [P01–P14证据导航](../evidence/P01-P14/README_zh-CN.md)
- [十四项总证据矩阵](../manuscripts/P01-P14_evidence_matrix_zh-CN.md)
- [中文运行手册](../reproducibility/RUNBOOK_zh-CN.md) / [English runbook](../reproducibility/RUNBOOK_EN.md)
- [中文平台矩阵](../reproducibility/PLATFORM_MATRIX_zh-CN.md) / [Runtime platform matrix](../reproducibility/PLATFORM_MATRIX_EN.md)
- [WSL双目录入口说明](../reproducibility/wsl/README.md)
- [公开核心软件与验证器](../software/README.md)
- [AI4S Agent能力与结果](../ai4s-agent/CAPABILITIES_AND_RESULTS_zh-CN.md)及[限制](../ai4s-agent/LIMITATIONS_zh-CN.md)
- [文件清单](../manifests/FILE_INVENTORY.md)与[SHA-256 manifest](../manifests/sha256-manifest.json)
