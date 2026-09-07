# WP4-B 六点成对先导与 Gate V2-4P 报告

状态：**PASSED**

估计量：`P12B_PHYSICAL_ISEII_ASE_0K`，`ASE=(C+D)-(A+B)`；正值为芳香、负值为反芳香。

与 P12-A 的关系：**INCOMPARABLE**，本报告不改写 P12-A，也不修改 v0.1.0/v0.2.0。

## 六点成对结果

| N | 系列 | 0 K ASE (kJ/mol) | 0 K ASE (kcal/mol) | 按±2阈值分类 | 身份 |
|---:|---|---:|---:|---|---|
| 8 | 4n | -34.294 | -8.196 | antiaromatic | selected paired-pilot minima |
| 10 | 4n+2 | -8.487 | -2.028 | antiaromatic（阈值敏感） | selected paired-pilot minima |
| 16 | 4n | 5.758 | 1.376 | nonaromatic_interval | selected paired-pilot minima |
| 18 | 4n+2 | 43.284 | 10.345 | aromatic | selected paired-pilot minima |
| 32 | 4n | -2.190 | -0.523 | nonaromatic_interval | selected paired-pilot minima |
| 34 | 4n+2 | 11.715 | 2.800 | aromatic | selected paired-pilot minima |

## Gate V2-4P

| Gate 条件 | 结果 |
|---|---|
| `all_six_N_defined` | PASS |
| `A_B_C_D_each_N` | PASS |
| `two_conformer_sources_and_identity_manifest` | PASS |
| `both_conformer_sources_actually_evaluated` | PASS |
| `runtime_failure_discovery_statistics` | PASS |
| `0K_ASE_all_six_N` | PASS |
| `lowest_verified_conformer_0K_all_six_N` | PASS |
| `closed_shell_and_BS_checks_for_4n_A_C` | PASS |

决定：**ELIGIBLE_FOR_SEPARATE_EXPANSION_APPROVAL**。

## 破缺对称敏感性

| N | 物种 | ΔE(UKS-RKS) (kcal/mol) | <S²> | 诊断 |
|---:|---|---:|---:|---|
| 8 | A | -0.000000 | 0.000000 | 坍缩至闭壳层根 |
| 8 | C | +0.000000 | 0.000000 | 坍缩至闭壳层根 |
| 16 | A | -0.000000 | 0.000000 | 坍缩至闭壳层根 |
| 16 | C | +0.000000 | 0.000000 | 坍缩至闭壳层根 |
| 32 | A | -0.079141 | 0.236347 | 非坍缩BS解 |
| 32 | C | +0.000001 | 0.000001 | 坍缩至闭壳层根 |

`N=32/A`存在比RKS低约`0.079 kcal/mol`且`<S²>=0.236`的非坍缩BS解；把这一差值作用到反应式只会把`N=32`的ASE从`-0.523`推向约`-0.444 kcal/mol`，仍位于预注册非芳香区间内。它必须作为状态敏感性保留，但不造成当前分类翻转。

## 解释边界

- 这是 8/10、16/18、32/34 三组成对先导，不是完整 N 序列。
- N=16/18/32/34 是 2025 年 Chemical Science 补充信息的外部锚点；N=8/10 才是本项目新增的 PySCF 计算。
- 每个N、每个A/B/C/D均已完成source与独立候选来源的实际评估，并在候选集合中确定最低已验证0 K构象；这正是`both_conformer_sources_actually_evaluated`和`lowest_verified_conformer_0K_all_six_N`通过的依据。
- ETKDG逐次“最后四次无新低能唯一构象”条件本身未单独满足，但预注册的CREST fallback已完成，因此总体`stop_rule_evidence_complete=true`、Gate停止证据闭合；两者不得混写为“ETKDG停止规则已满足”。
- `N=10`的`-2.028449 kcal/mol`仅越过预注册`-2.0`边界约`0.028449 kcal/mol`，因此标记为阈值敏感，不能作为稳健反芳香判据。
- 破缺对称计算只诊断闭壳层敏感性，不自动生成芳香性标签。
- Gate V2-4P是数据完整性与扩展准备门禁，不是P12-B科学命题终判。通过只表示可以另行审议扩展授权，并不自动授权扩展，也不等同于已经证明尺寸无关的普遍定律。
