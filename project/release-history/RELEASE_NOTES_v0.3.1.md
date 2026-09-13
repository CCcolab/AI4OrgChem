# AI4OrgChem v0.3.1 — Post-Review Evidence Maintenance

> **Historical record / 历史记录（2026-09-08）：** This note describes the fixed `v0.3.1` release, not the current release. Its original P12 cross-estimand onset rationale was withdrawn by the later [v0.3.2 P12 corrigendum](../../P12_CORRIGENDUM.md). The historical 13+1 machine classification remains unchanged; no new P12 verdict is implied. For the current release, see the [v0.3.2 notes](../../RELEASE_NOTES_v0.3.2.md).
>
> **中文提示：** 本文记录固定的`v0.3.1`历史版本，并非当前发布说明。原 P12 跨估计量起点差理由已由[后续勘误](../../P12_CORRIGENDUM.md)撤回；13+1机器分类仍保留为历史记录，不据此作新的P12判定。当前版本请见[`v0.3.2`发布说明](../../RELEASE_NOTES_v0.3.2.md)。

## English

`v0.3.1` is a post-review scientific-evidence maintenance release. It preserves the immutable `v0.3.0` scientific-closure package while incorporating qualified evidence and cross-document corrections completed after that release.

### Scientific classification recorded at v0.3.1 publication (historical)

- 14 propositions have determinate proposition-level classifications.
- 13 are consistent with the corresponding monograph propositions within their registered tested domains.
- P12 was labeled partially consistent. The original rationale based on comparing size onsets across different estimands is superseded by the v0.3.2 corrigendum; the historical label is retained without a new whole-proposition decision.
- 0 are globally inconsistent and 0 are unknown.

### Changes incorporated

1. **P14 evidence eligibility:** the STO-3G technical pilot is explicitly ineligible for scientific classification. A B3LYPG/6-31G(d) production optimization passed all registered gates and gives `dDelta-r=0.172204 A` and `+67.679719 kcal/mol`. The separate fixed-geometry source-level anchor remains `+67.086899 kcal/mol`.
2. **P11-B source-2007 recalculation:** ten cyanobenzene and three benzene states were optimized independently under hard all-atom planarity and the source-2007 state-specific restricted protocol. The resulting `CE=+1.173122` and `IE=+0.490079 kcal/mol` support the monograph within this single-system tested domain. The older fixed-geometry opposite-sign result remains an audit record.
3. **P05 seven-angle continuation:** the same molecular system and estimator were evaluated at 0°, 5°, 10°, 17°, 25°, 35°, and 45°. All six nonzero endpoints are positive; the maximum closure residual is `3.493205724681e-12 Eh`.
4. **P07 independent path audit:** existing 0°/17° G/FUD/DSI2/PDSI/FUL results sharing the same RHF/STO-3G Hamiltonian were audited. The omitted bridge exactly explains the naive three-term residual, and the path-complete energy identity closes at both angles. P07 evidence identity is `INDEPENDENT_COMPUTATIONAL_AUDIT_PLUS_DERIVED_SYNTHESIS`.

### Boundaries

- This release does not claim that traditional organic chemistry is globally wrong or establish a universal opposite law.
- The associated manuscript has not undergone peer review.
- Source-proxy status, estimator identity, tested scope, and evidence independence remain explicit.
- The small engineering dataset does not establish industrial-scale generalization.
- OpenAI Codex (GPT-5.6) assisted research engineering; Xiao Chen retains authorship, scientific decisions, interpretation, and publication responsibility. OpenAI is not a scientific certifier or institutional endorser.

## 中文

`v0.3.1`是复评后的科学证据维护版本。它保持`v0.3.0`科学闭合包不可变，并纳入其发布后完成的合格证据和跨文档一致性修正。

### v0.3.1发布时记录的科学分类（历史）

- 十四项命题均已获得确定性命题级分类；
- 十三项在各自注册受测域内与原著对应命题一致；
- P12当时标为部分一致；原先借不同估计量的起点差支持这一标签的理由已由v0.3.2勘误撤回。历史标签继续保留，但不构成新的整项判定；
- 整体不一致0项，未知0项。

### 本版纳入的更新

1. **P14证据资格：** STO-3G技术烟测被明确排除在科学定判证据之外。B3LYPG/6-31G(d)生产优化通过全部注册门禁，得到`dΔr=0.172204 Å`和`+67.679719 kcal/mol`；独立的固定几何原著层级锚点仍为`+67.086899 kcal/mol`。
2. **P11-B source-2007复算：** 氰基苯十态和苯三态在全原子平面硬约束及source-2007逐状态受限协议下分别优化，得到`CE=+1.173122`、`IE=+0.490079 kcal/mol`。P11在该单体系受测域内更新为一致；旧固定几何异号结果继续作为审计记录。
3. **P05七角度增强：** 在同一分子体系和同一估计量下完成0°、5°、10°、17°、25°、35°、45°序列。六个非零角度端点全部为正，最大闭合残差为`3.493205724681e-12 Eh`。
4. **P07独立路径审计：** 对共享同一RHF/STO-3G哈密顿量的0°/17° G/FUD/DSI2/PDSI/FUL既有结果进行审计。遗漏的桥接项精确解释天真三项残差，路径完整恒等式在两点均闭合。P07证据身份更新为`INDEPENDENT_COMPUTATIONAL_AUDIT_PLUS_DERIVED_SYNTHESIS`。

### 边界

- 本版不宣称传统有机化学整体错误，也不建立反方向的普遍定律；
- 相关论文稿尚未经过同行评审；
- source-proxy身份、估计量、受测范围和证据独立性继续明确列示；
- 小规模工程数据集不支持工业级泛化结论；
- OpenAI Codex（GPT-5.6）提供研究工程辅助；Xiao Chen承担作者身份、科学决策、结果解释和发布责任。OpenAI不作为科学认证方或机构背书方。
