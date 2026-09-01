# Gate V2-0 最终判定与 WP1/WP3 授权记录

- 日期：2026-09-01
- Gate：`V2-0`
- 最终状态：`PASSED`
- 判定角色：项目负责人（未宣称独立专家签署）
- 科学作业启动数：`0`
- V0.1 科学结论改写数：`0`

## 判定依据

Gate V2-0 的 11 项合同、边界、密封、审计和实现准备检查全部通过。机器可读判定见 `configs/science_v0.2/wp0_gate_final_decision.json`；工作包授权与 Gate 判定分离，见 `configs/science_v0.2/wp_authorizations.json`。

已接受的四项评审决策为：

1. WP1 唯一主高等级锚点为 Quantum Package v2.2.2 的 CIPSI+PT2；
2. WP3 在 V2-0 冻结对称适配种子，在获授权后的 V2-3 计算 Hessian 并比较本征子空间；
3. WP3 电子结构干预固定为三种 Kekulé 片段的 conditional-SCF；
4. WP4 双支路协议作为 Gate 定义被接受，但 WP4 计算未获授权。

## 独立授权结果

| 工作包 | 当前状态 | 本次是否允许科学计算 | 是否已经启动 |
|---|---|---:|---:|
| WP1 | `AUTHORIZED_TO_START` | 是；仅限 P09-B/CBD 多参考稳健性合同 | 否 |
| WP2 | `HOLD` | 否；仍缺合法 ORCA 环境及三程序对齐烟测 | 否 |
| WP3 | `AUTHORIZED_TO_START` | 是；包括 Hessian、模式子空间与 conditional-SCF 干预 | 否 |
| WP4 | `HOLD` | 否；仍需昂贵配对先导集的单独授权 | 否 |
| WP5 | `SCHEMA_AND_INTERNAL_SAMPLE_ONLY` | 不涉及科学计算 | 否 |
| WP6 | `HOLD` | 否；V0.2 发布候选尚未授权 | 否 |

## 启动前强制条件

WP1 和 WP3 虽已获启动授权，但首个科学作业前仍必须分别冻结并密封输入包，记录 Cartesian 坐标、方法、基组、状态/根、阈值、随机种子与资源上限。资源并发规则保持为：同一时刻只运行一个中高内存量子化学作业。

## 边界声明

本判定只关闭 Gate V2-0 并开放 WP1/WP3 的执行资格，不等于产生任何新的科学结果，也不自动改变 V0.1 的十四项结论。WP1 只能建立 P09-B 的自身证据；WP3 只能建立 P10-B 的自身机制证据，均不得自动升级对应 A 命题。
