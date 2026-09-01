# WP0 开源量化环境建立记录

- 环境：`ai4orgchem-v02-qm-open`
- 发行版：WSL2 `Ubuntu-24.04`
- 状态：`CREATED_IMPORT_VALIDATED`
- 旧环境修改：`0`

## 冻结核心版本

| 组件 | 版本 |
|---|---:|
| Python | 3.12.14 |
| Psi4 | 1.11 |
| PySCF | 2.14.0 |
| NumPy | 2.5.2 |
| SciPy | 1.18.0 |
| h5py | 3.16.0 |
| jsonschema | 4.23.0 |

所有模块实际路径均位于 `${HOME}/micromamba/envs/ai4orgchem-v02-qm-open/`。运行必须设置 `PYTHONNOUSERSITE=1`，防止用户级 `~/.local` 污染。

安装时首次发现 pip 会把用户级 PySCF 误判为已满足；已停止依赖覆盖，改为在 `PYTHONNOUSERSITE=1` 下用 `--no-deps` 安装 PySCF wheel，并使用 conda 的 NumPy/SciPy/h5py。最终导入和路径检查均通过。

本记录只证明程序可导入，不证明 PySCF/Psi4 的 Gaussian-style B3LYP 数值已经等价。跨程序水/乙烯功能定义烟测仍未运行，WP2 保持 HOLD。ORCA 未安装，且不得绕过许可证边界。
