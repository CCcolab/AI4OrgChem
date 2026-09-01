# WP0：WP1 多参考接口能力探测

日期：2026-09-01  
状态：`PARTIAL CAPABILITY / WP1 HOLD`  
科学计算：`未启动`

在新隔离环境 `ai4orgchem-v02-qm-open` 中仅执行 Python 模块导入探测，没有创建分子、SCF 对象或能量任务。

结果：

- PySCF 2.14.0 的 `mcscf`、`mrpt.NEVPT` 和 `fci.selected_ci` 接口存在；
- `shciscf` 接口不存在；
- CASSCF/SC-NEVPT2 敏感性阶梯具备后续实现基础，但尚未执行验证；
- PySCF 内置 selected-CI 接口不自动等同于预注册的“带 PT2 修正与外推不确定度”的主高等级锚点；
- ORCA 仍未找到，许可边界未闭合。

因此本探测本身不提高 P09-B 的科学等级，也不满足 WP1 主锚点门禁。后续已在另一隔离环境中建立并烟测 Quantum Package/CIPSI 主锚点实现；见 `WP0_QP22_CIPSI_ENVIRONMENT_2026-09-01.md`。两项记录不得合并为 CBD 科学结果。Gate 最终通过后 WP1 已另行授权启动，但尚未运行；当前状态以 `configs/science_v0.2/wp_authorizations.json` 为准。
