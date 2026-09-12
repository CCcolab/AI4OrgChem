# 典型程序复算与证据核验入口

[English](TYPICAL_PROGRAMS.md)

本页帮助化学、量子化学和计算化学读者选择一个可控入口，观察AI4OrgChem如何把**科学问题、冻结协议、电子结构计算、数值门禁、机器结果和范围化结论**连接成可审计流程。

> 本页中的“核验”不表示认证原著理论。`PASS`只表示指定程序在登记输入、方法和容差内完成了相应计算或一致性检查。

## 先选择运行层级

| 层级 | 入口 | 是否运行QM | 典型资源 | 当前状态 | 适合读者 |
|---|---|---:|---|---|---|
| L0 | P01–P14冻结证据核验 | 否 | 普通Python，数秒 | **可运行** | 所有读者 |
| L1 | P09条件SCF核心测试 | 小型测试 | CPU，通常数分钟 | **可运行** | 方法与程序审查者 |
| L2 | P14固定几何技术烟测 | 是，STO-3G | WSL2、8线程 | **可运行** | 首次QM体验 |
| L3 | P14固定几何科学层级复算 | 是，B3LYPG/6-31G(d) | WSL2、8线程、充足内存 | **可运行** | 量子化学复核 |
| L4 | P14五参数生产优化 | 是，高成本 | WSL2、8线程、至少13 GiB可用内存 | **可运行；高级** | 深度独立复算 |

P09环丁二烯烟测、P10苯BLA扫描和P09完整芳香能复算是下一批公开封装对象。它们的科学设计已冻结，但在完成独立输出目录、依赖补齐和洁净克隆实跑前，本页不提供可能误导用户的伪命令。

## 统一准备

权威科学平台是 **WSL 2 / Ubuntu 24.04**。从GitHub克隆或下载Release完整包后，在仓库根目录执行：

```bash
micromamba create -f reproducibility/environment.yml  # 仅在环境不存在时
source reproducibility/wsl/activate-ai4orgchem-public.sh
cd software
python -m pip install -e ".[science,test]"
cd ..
```

环境创建、平台差异和安全边界见[中文运行手册](RUNBOOK_zh-CN.md)与[平台矩阵](PLATFORM_MATRIX_zh-CN.md)。所有复算输出写入被Git忽略的`runs/reproduction/`；不得覆盖`evidence/`中的冻结证据。

---

## L0：P01–P14冻结证据核验

### 科学目的

确认十四项公开结果文件可以被读取，命题编号、判定、证据引用和关键状态彼此一致。该入口不重新运行量子化学，不证明计算物理正确，只检查发布证据包的内部完整性。

### 计算过程

1. 枚举P01–P14机器结果；
2. 检查JSON/JSONL结构和命题编号；
3. 检查冻结分类与总表统计；
4. 检查P11、P12、P14等关键边界状态；
5. 输出命题数、通过数和总状态。

### 运行

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
```

### 预期输出与判读

预期包含`status: PASS`、`propositions_checked: 14`和`propositions_navigated: 14`。若失败，应先阅读错误指出的具体文件，不得通过修改验证器来迁就结果。

### 边界

该入口核验的是**已经发布的证据记录**，不是原始量子化学复算，也不是同行评审。

---

## L1：P09条件SCF核心实现测试

### 科学目的

检查P09/P14所用source-aligned条件SCF基础设施是否按定义处理AO的σ/π身份、片段边界、Fock/overlap屏蔽、交换积分类别和独立能量组装。

### 计算过程

1. 构造小型测试矩阵或PySCF AO对象；
2. 根据分子平面和AO方向把基函数分类为σ或π；
3. 给π轨道附加局域片段标签；
4. 将登记的跨片段Fock和overlap块置零；
5. 应用冻结的15类交换型二电子积分规则；
6. 迭代条件SCF；
7. 独立组装单电子、库仑、交换和核排斥分量；
8. 检查电子数、能量闭合、广义对易子和密度幂等性。

### 运行

```bash
cd software
python -m pytest -p no:cacheprovider \
  tests/test_p09_conditional_scf.py \
  tests/test_p09_energy_assembly.py \
  tests/test_p09_eri_mask.py
cd ..
```

### 预期输出与判读

pytest应全部通过。失败表示公开核心算法、运行库或平台出现差异，不能据此继续解释P09/P14科学结果。

### 边界

单元测试证明代码满足登记的局部数学合同；它不等同于苯ESE或环丁二烯ADE的完整分子复算。

---

## L2：P14固定几何技术烟测

### 科学目的

用较小的STO-3G基组确认C12H6体系、几何重建、AO分类、条件SCF和能量账本可以在用户机器上完整执行。

### 计算过程

1. 从原著公开的五个结构参数分别重建G和PLG的平面D3h `source-proxy`几何；
2. 在G几何运行普通闭壳层RKS；
3. 在PLG几何运行普通RKS，获得条件态初始密度；
4. 对PLG执行AO σ/π分类和片段映射；
5. 应用条件Fock/overlap及交换积分规则并收敛条件SCF；
6. 计算`E(ordinary@G)-E(conditional-PLG@PLG)`技术端点；
7. 检查78电子、SCF收敛、几何重建、能量闭合、对易子和幂等性。

### 运行

```bash
python software/scripts/run_p14_benzotricyclobutadiene_smoke.py
```

默认输出：

- `runs/reproduction/p14/p14_benzotricyclobutadiene_fixed_geometry_smoke_v0.1.json`
- `runs/reproduction/p14/p14_benzotricyclobutadiene_fixed_geometry_smoke.md`

### 预期输出与判读

`smoke_gate_verdict`应为`PASS`。数值可以用于检查实现和平台，但**不得**作为P14科学定判值，因为STO-3G不是登记的生产层级。

---

## L3：P14固定几何科学层级复算

### 科学目的

在B3LYPG/6-31G(d)层级，对公开的G/PLG `source-proxy`几何重算P14固定几何端点，并把用户结果与冻结值`67.086899 kcal/mol`比较。

### 计算过程

1. 读取并哈希公开G、PLG输入；
2. 验证五参数重建、原子顺序、平面性和78电子；
3. 计算普通G态；
4. 计算普通PLG锚点并形成初始密度；
5. 计算source-aligned条件PLG态；
6. 独立复核直接实现和内存受控实现的总能等价性；
7. 组装固定几何端点；
8. 检查方法、基组、SCF、电子数、能量闭合、对易子、幂等性和内存门禁。

### 运行

```bash
python software/scripts/run_p14_benzotricyclobutadiene_source_level_fixed_geometry.py
```

默认输出位于`runs/reproduction/p14/`。公开冻结输入及其身份说明见[P14输入说明](../evidence/P01-P14/P14/inputs/README.md)。

### 预期输出与判读

只有全部门禁通过时，该复算才可与冻结固定几何端点比较。小的末位差异应结合PySCF、BLAS和数值积分版本报告，不得静默改写容差。

### 边界

原著未公开完整历史Cartesian坐标；这里复算的是公开五参数重建的`source-proxy`，不是历史原厂程序身份复现。

---

## L4：P14五参数生产优化

### 科学目的

分别优化普通G态和条件PLG态的五个平面D3h结构参数，检查结构响应`dΔr(GP)`和优化能量端点是否同时满足P14资格门禁。

### 计算过程

1. 检查至少13 GiB可用内存和单任务运行约束；
2. 从冻结五参数生成G、PLG初始结构；
3. 在B3LYPG/6-31G(d)层级优化普通G态；
4. 检查优化终止原因、最大梯度和活动边界；
5. 在同一层级优化条件PLG态；
6. 再次检查SCF、78电子、最大梯度、活动边界和条件态数值闭合；
7. 计算`dΔr(GP)`及优化端点；
8. 只有全部资格项通过，才生成`production_gate_verdict: PASS`。

### 运行

```bash
python software/scripts/run_p14_benzotricyclobutadiene_production_optimization.py
```

该程序具有检查点，默认结果和报告写入`runs/reproduction/p14/`。运行期间不要并行启动其他中高内存QM作业。

### 预期输出与判读

冻结参考为：

- `dΔr(GP) = 0.172204 Å`；
- 优化端点`67.679719 kcal/mol`。

数值接近并不自动等于通过；方法、基组、收敛、梯度、边界、电子数和能量闭合必须全部合格。

### 边界

该优化只覆盖登记的平面D3h五参数子空间，不宣称完成全笛卡尔频率、更宽对称性搜索、19分子面板或普遍应变芳香规律。

---

## 下一批入口的启用门禁

以下三个程序具有很高的展示价值，但只有完成全部门禁后才会在本页标记为“可运行”：

### P09环丁二烯固定几何烟测

流程：固定平面矩形几何 → 普通G-like RKS → AO σ/π分类 → 两片段条件DSI SCF → 15类交换积分处理 → 独立能量账本 → 12项数值门禁。它只检验同一几何上的实现闭合，不替代最终VDE/ADE。

### P10苯BLA—核排斥扫描

流程：读取同协议P09 G/GL端点 → 分解`ΔEe`与`ΔEN` → 固定平均C–C及C–H长度 → 在`δ=0、0.01、0.02、0.04、0.06 Å`计算普通RKS → 独立核间库仑和 → 曲率与正负δ对称性检查。它支持受测路径上的机制分析，不单独证明普遍“核排斥主导”。

### P09完整苯/环丁二烯复算

流程：环丁二烯G优化与同几何DSI → 条件GL优化 → VDE/ADE组装；苯G优化与三片段DSI → GL与GE1受限优化 → `ESE=ΔEA-3ΔEA1` → 与盲冻结锚点比较。完整程序必须保留检查点、单任务资源限制和失败即停止策略。

启用前必须满足：脚本和配置进入精选包、所有输出重定向到`runs/reproduction/`、补齐geomeTRIC依赖、无私有路径或密钥、运行时资源说明完整、单元测试通过、WSL2洁净克隆实跑通过、结果与冻结证据在登记容差内一致。

## 如何提交独立复算结果

提交Issue时请附：仓库标签或提交哈希、操作系统、Python/PySCF版本、CPU线程、内存、实际命令、输出JSON的SHA-256、`PASS/FAIL`状态及与冻结值的残差。失败结果同样有科学价值，不应删除或只提交成功截图。
