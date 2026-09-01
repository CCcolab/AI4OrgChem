# WP1 / Gate V2-1：环丁二烯普通物理态多参考稳健性

- Gate：`PASS_WITH_METHOD_SENSITIVITY`
- P09-B结论：`PARTIALLY_SUPPORTED`，证据等级`R2`
- 与V0.1 P09-A关系：`COMPLEMENTARY`，不自动改写条件态ADE/VDE

## 势垒结果（D4h − D2h）

| 方法 | kcal/mol |
|---|---:|
| B3LYP_RKS_kcal_mol | 25.912485 |
| CAS_4_4_SC_NEVPT2_kcal_mol | 8.082905 |
| CAS_12_12_SC_NEVPT2_kcal_mol | 7.399598 |
| QP_CIPSI_Evar_plus_PT2_kcal_mol | 48.407308 |
| QP_reported_extrapolation_subset_kcal_mol | 46.369028 |

所有受测方法给出正势垒，且D4h自然占据数显示明显双自由基/多组态特征；但不同方法的势垒幅度离散很大。故V0.2支持的是P09-B的定性物理图像，不发布单一方法无关的精确势垒。

Quantum Package主锚点在预注册行列式上限附近仍有较大剩余PT2，因此其E+PT2和外推序列作为高等级敏感性证据保留，不能冒充已收敛FCI。失败启动、环境修复和原始日志均保留。

## English conclusion

All tested ordinary-state methods place the D4h stationary point above the D2h minimum and diagnose strong D4h multireference character. WP1 therefore partially supports P09-B at R2, while the quantitative barrier remains method-sensitive. This evidence is complementary to, not a direct upgrade of, the P09-A conditional-state estimand.
