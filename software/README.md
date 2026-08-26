# 精选软件

本目录只收纳具有公开复核价值的LFMO/条件SCF核心实现、对应测试和自包含验证入口。内部阶段编排、日志、缓存和依赖未公开开发树的数据生成脚本不进入GitHub包。

## 内容

- `src/ai4orgchem/lfmo/`：非正交子空间、反射适配、状态掩码、KOST与GL辅助实现；
- `src/ai4orgchem/qm/`：AO分类、ERI掩码、条件SCF与独立能量组装；
- `tests/`：与上述公开模块直接对应的64项测试；
- `scripts/validate_public_evidence.py`：检查P01–P14机器结果与冻结判定；
- `scripts/validate_evidence_navigation.py`：检查双语14项导航、120个以上证据链接及P11/P12差异数值。
- `scripts/validate_wsl_release.py`：检查WSL双目录模式、公开环境名、平台边界和无环境变更约束。
- `scripts/validate_release_package.py`：执行JSON/JSONL/YAML/CFF语法、Markdown链接、SHA清单、敏感信息、路径、大文件和重复文件总门禁。
- `scripts/refresh_release_snapshot.py`：在授权修改后重建实质文件清单和SHA-256快照；刷新后必须重新运行全部门禁。

## 验证命令

在仓库根目录运行：

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```

安装与完整测试方法见[中文运行手册](../reproducibility/RUNBOOK_zh-CN.md)或[英文运行手册](../reproducibility/RUNBOOK_EN.md)。项目权威科学环境为WSL 2 / Ubuntu 24.04；原生Windows仅作为有限复核平台，不被声明为PySCF、MACE/NequIP或PySR历史结果的等价运行环境。

本目录不包含原著程序，也不承诺仅凭首版精选包重做全部昂贵量子化学计算。
