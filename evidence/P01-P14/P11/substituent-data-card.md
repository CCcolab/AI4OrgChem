> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P11-B 氰基苯取代基效应数据卡 v0.1

## 范围

- 体系：cyanobenzene `C7H5N`与定义所需的同协议benzene锚点。
- 方法：PySCF `B3LYPG/6-31G(d)`，source-2007 Fock/one-electron/overlap屏蔽，无ERI删除。
- 几何：氰基苯使用论文Figure 7逐态重原子键长重构；苯使用主文Figure 3和官方Supporting Information的Z-matrix数据。
- 原著程序代码：未使用。

## 输出

- `ESE(SB)=-38.399223 kcal/mol`；
- `ESE(Ph)=-39.580151 kcal/mol`；
- 共轭贡献`CE=+1.180928 kcal/mol`，与原著`+1.2`一致；
- 同实现苯锚点`ESE=-39.244437 kcal/mol`；
- 诱导贡献`IE=-0.335714 kcal/mol`，与原著`+0.49`符号不一致。

## 质量与判定

- 氰基苯84/84项、苯锚点12/12项计算门禁通过；
- 专用验证器：`PASS_P11B_SCOPED_SUBSTITUENT_EFFECT_RELEASE`；
- 科学判定：`P11B_CONJUGATIVE_CONSISTENT_INDUCTIVE_INCONSISTENT_UNDER_SOURCE_PROXY`；
- 分类：共轭项一致；诱导项在冻结Figure 7 source-proxy下与原著异号，判为不一致；缺失完整历史Cartesian坐标仅限制历史身份声明。

本数据不得作为普遍取代基定律、生产标签或AI训练标签。
