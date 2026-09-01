# WP0 密封输入包演练

- 演练 ID：`WP0-BLIND-DRILL-001`
- 日期：2026-09-01
- 性质：**非科学、仅验证打包和先哈希后比较顺序**
- 网络策略：`DENY`
- 仓库策略：`BUNDLE_ONLY_NO_FULL_REPOSITORY`

| 对象 | SHA-256 |
|---|---|
| `blind_input_bundle.zip` | `8ba36fa12b984037c9f2270fc382a43242a8ed86dc2bba20a1b6d364b2f87611` |
| 冻结计算脚本 | `bc7c3ba0707617443fc2b616df4f85f2740352a9982362527efe957984b4c43d` |
| 首轮结果 | `f28a2ef30ebfef79d2d357d1bab8d7a1b658871dfac839153f73c634acfcaa5e` |

输入明确标记 `scientific_data=false`，不含原著数值、V0.1 判定或量子化学结构。该演练证明当前文件布局能够记录 bundle、脚本和首轮结果三次承诺，但不证明科学盲法已经完成，也不授予 WP1–WP4 权限。

## 运行时隔离演练

随后在 WSL2 用户、mount 与 network namespace 中运行同一非科学夹具。机器记录为：

- 无非回环地址；
- 无网络路由；
- 以空目录 bind-mount 遮蔽完整项目仓库；
- 工作目录仅含允许输入与演练脚本；
- 计算器退出码为 0，结果仍标记 `scientific_data=false`。

机器记录：`runs/science_v0.2/wp0_blind_isolation/isolation_record.json`。

首次实现曾因仅按接口名称判断而将残留接口视为失败；项目保持该失败事实，并将判据改为实际网络可达性所需的“无非回环地址且无路由”。重跑时接口列表仅含 `lo`，全部检查通过。

后续科学盲法必须在独立工作目录或容器中重复本顺序，并由不同 evaluator 挂载目标值。
