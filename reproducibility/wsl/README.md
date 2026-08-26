# WSL 2 entry points / WSL 2 运行入口

These scripts support two layouts without embedding a user name or modifying an existing environment:

1. **GitHub clone:** run the scripts directly under `reproducibility/wsl/`; the repository root is detected automatically.
2. **FHS deployment:** install the repository at `/opt/ai4orgchem/publication`; that path is used only when a clone root cannot be detected.

中文说明：两个脚本同时支持GitHub克隆目录和`/opt/ai4orgchem/publication`部署目录，不硬编码用户名，也不会自动创建、更新或覆盖任何现有环境。

## Verify frozen evidence / 验证冻结证据

From the repository root:

```bash
bash reproducibility/wsl/ai4orgchem-verify
```

An explicit deployment root can be selected without editing the scripts:

```bash
AI4ORGCHEM_PUBLICATION_ROOT=/opt/ai4orgchem/publication \
  bash reproducibility/wsl/ai4orgchem-verify
```

## Activate the public review environment / 激活公开复核环境

First inspect existing environments:

```bash
micromamba env list
```

Only when `ai4orgchem-public` is absent, create it explicitly:

```bash
micromamba create -f reproducibility/environment.yml
```

Then source the activation entry point:

```bash
source reproducibility/wsl/activate-ai4orgchem-public.sh
```

The activation script stops if the named environment is absent. It never performs `update`, `install`, `remove`, or forced replacement operations. If these files are copied through a system deployment process, preserve executable permissions with `chmod +x reproducibility/wsl/*`.

激活脚本在环境不存在时会停止并提示，不会擅自变更用户已有的WSL 2环境。完整边界见上一级运行手册和平台矩阵。
