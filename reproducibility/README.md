# 公开复现

本目录提供平台中立的CPU环境和明确运行手册：

- `environment.yml`：Python、NumPy、SciPy、PyYAML、pytest及PySCF的最小环境；
- `RUNBOOK_EN.md` / `RUNBOOK_zh-CN.md`：冻结证据验证、公开软件测试和适用边界；
- `PLATFORM_MATRIX_zh-CN.md` / `PLATFORM_MATRIX_EN.md`：WSL 2权威环境、原生Windows边界及GPU运行时隔离说明。
- `wsl/`：支持GitHub克隆目录与`/opt/ai4orgchem/publication`部署目录的可移植Shell入口。

首版保证处理后证据可核查、公开核心代码可测试；科学与GPU结果的权威平台为WSL 2 / Ubuntu 24.04，不把原生Windows、开发机器镜像、GPU缓存或私有运行目录伪装成等价复现条件。

两个WSL入口不会自动创建、更新、删除或覆盖现有环境；环境不存在时必须由使用者检查后显式创建。
