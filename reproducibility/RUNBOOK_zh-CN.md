# GitHub精选包复现说明

本说明只覆盖GitHub精选包内可独立执行的内容，不假定存在本地开发日志、原著全文、历史程序、原始量化输出或私有API凭据。

## 权威运行平台

本项目科学计算的权威执行环境是 **WSL 2 / Ubuntu 24.04**。原生Windows可用于阅读文档、检查JSON和执行统一证据验证器，但不被声明为PySCF量化主线、MACE/NequIP CUDA训练或PySR/Julia搜索的等价复现环境。详细边界见 `PLATFORM_MATRIX_zh-CN.md`。

## 1. 快速验证冻结证据

在精选包根目录执行：

```bash
python software/scripts/validate_public_evidence.py
```

预期输出为 `status: PASS`、`propositions_checked: 14`。这项检查验证P01–P14处理后结果的文件完整性与冻结判定，不重新运行昂贵量子化学计算。

## 2. 安装并测试公开核心软件

建议先从Windows PowerShell进入已安装的WSL发行版，再在克隆目录内操作：

```powershell
wsl -d Ubuntu-24.04
```

在WSL中创建项目专用环境。不得覆盖已有WSL环境；如果`ai4orgchem-public`已存在，应先检查或改用新的环境名，不执行强制更新。

```bash
micromamba env list
micromamba create -f reproducibility/environment.yml  # 仅在该环境不存在时执行
source reproducibility/wsl/activate-ai4orgchem-public.sh
cd software
python -m pip install -e ".[science,test]"
python -m pytest -p no:cacheprovider
```

`science`可选依赖包含PySCF。CPU即可运行单元测试；重做完整科学计算所需的输入、资源和历史环境不属于首版精选包承诺。

## 3. 环境边界

- `environment.yml`提供WSL/Linux优先的CPU复核环境，不是本地机器镜像，也不包含MACE与NequIP的相互冲突运行时；
- MACE、NequIP、PySR训练结果在Agent评估摘要中披露，但模型、缓存和内部运行目录不进入首版GitHub包；
- 原著、预印本、扫描件及受版权保护的全文材料不随项目发布。

## 4. WSL入口的两种目录模式

- GitHub克隆模式：脚本从`reproducibility/wsl/`自动识别仓库根目录；
- FHS部署模式：无法识别克隆根目录时，才回退到`/opt/ai4orgchem/publication`；
- 可通过`AI4ORGCHEM_PUBLICATION_ROOT`显式指定根目录，不需要修改脚本；
- 激活入口只检查并激活`ai4orgchem-public`，不会自动创建、更新、删除或覆盖环境。

运行冻结证据和WSL边界检查：

```bash
bash reproducibility/wsl/ai4orgchem-verify
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```
