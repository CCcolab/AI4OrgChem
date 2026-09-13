# AI4OrgChem v0.3.2 — P12 Evidence-Interpretation Corrigendum

## English

`v0.3.2` is a documentation and evidence-interpretation maintenance release. It adds no quantum-chemical calculations, changes no frozen P12 machine result, and does not reclassify P12. The `v0.3.1` tag, complete archive and checksum remain immutable.

### P12 correction

The **13 consistent and 1 partially consistent (P12)** count is the historical `v0.3.1` published classification, retained in the machine records for traceability. Under the project's three-way rule, a newly justified “partially consistent” verdict would require both an established supporting and an established opposing subclaim. The former rationale that treated different CESE and ASE onset sizes as an opposing subclaim is invalid: CESE and ASE are different estimands, so their reported boundaries are not a same-definition contradiction. Missing independent coverage is not a negative result. This correction does not automatically upgrade P12 to “consistent” either.

The six published N12/N14/N16/N18/N20/N22 values have an arithmetic and internal-ledger size-trend check, **not** six-point independent quantum-chemical reproduction. Existing local specified-configuration N12/N14/N16 candidate calculations offer limited directional compatibility but have not established full identity with the 2011 method or covered N18/N20/N22. Their numerical results are **not packaged here as new publicly reproducible evidence**. Independent ASE/ISE-II evidence complements the broad large-ring trend but cannot confirm or refute the precise CESE N=16/18 onset. The reviewed record establishes neither a same-estimand counterexample nor independent confirmation of that precise onset.

In plain language, the broad direction is compatible; the precise size boundary remains open. Different studies can report different boundaries under different descriptors, states, geometries and criteria. This is a substantive evidence boundary, not a last-decimal difference between programs. See the [bilingual P12 corrigendum](P12_CORRIGENDUM.md) and [evidence matrix](manuscripts/P01-P14_evidence_matrix_zh-CN.md).

### Package and limits

- The bilingual homepage, evidence indexes, matrix, expert review guides, publication positioning, project summaries, citation metadata, validators, file inventory and SHA-256 manifest are synchronized with this interpretation.
- No new SCF, gradient, optimization, Hessian, CESE or ASE job, historical-method identity claim, whole-proposition classification decision, or production-label authorization is included.
- The N16 source-coordinate fixed-geometry electronic-energy check remains a local program diagnostic, not a CESE/ASE or chemical-state-identity verdict.
- For a fixed offline review, download `AI4OrgChem-v0.3.2-complete.zip` and `AI4OrgChem-v0.3.2-complete.zip.sha256` from this Release's **Assets** and verify the checksum. **Code → Download ZIP** is a changeable `main` source snapshot, not the complete fixed Release asset.
- The associated manuscript has not undergone peer review. OpenAI Codex assisted engineering; Xiao Chen retains scientific and publication responsibility. OpenAI is not a scientific certifier or institutional endorser.

## 中文

`v0.3.2` 是**文档与证据解释维护版**：不增加量子化学计算，不改 P12 冻结机器结果，也不改判 P12。`v0.3.1` 标签、完整归档及校验文件保持不变。

### P12 勘误

“**13项一致、P12一项部分一致**”是 `v0.3.1` 的**历史发布分类**，机器记录继续保留以便追溯。按项目三分规则，要重新证成“部分一致”，须同时有已成立的支持子项和反对子项。原先把 CESE 与 ASE 报告的起始尺寸差异当成反对子项，依据不成立：两者不是同一估计量，其尺寸边界差异不是同口径反证；独立覆盖不足也不等于反面结果。本勘误同样不自动把 P12 升级为“一致”。

原著 N12/N14/N16/N18/N20/N22 六点公开表值已经过算术和源账本内尺寸变化核验，**不是**六点独立量化复算。已有 N12/N14/N16 指定构型的本地候选计算只提供有限方向相容性，尚未证明与原著 2011 方法完全同一，也未覆盖 N18/N20/N22；其数值**未作为本版新增公开可复核证据打包**。独立 ASE/ISE-II 可补充大环总体趋势，却不能确认或反证精确 CESE N=16/18 起点。现有已审记录既未建立同估计量反例，也未独立确认该精确起点。

通俗地说：**总体方向相容，精确尺寸边界仍待检验。** 不同文献可能因指标、状态、构型和判据不同而给出不同边界；这是实质证据边界，不是程序末位小数差异。详见[双语 P12 勘误](P12_CORRIGENDUM.md)及[总证据矩阵](manuscripts/P01-P14_evidence_matrix_zh-CN.md)。

### 发布包及限制

- 中英文首页、证据索引、矩阵、专家核验指南、发布定位、项目摘要、引用信息、验证器、文件清单与 SHA-256 清单已按上述解释同步。
- 本版没有新增 SCF、梯度、几何优化、Hessian、CESE 或 ASE 作业，也不宣称历史方法完全同一、不作整项新判定、不开放生产标签。
- N16 源坐标固定几何电子能检查仍是本地程序诊断，不是 CESE/ASE 或化学态同一性判决。
- 固定离线复核请从本 Release 的 **Assets** 下载 `AI4OrgChem-v0.3.2-complete.zip` 及 `AI4OrgChem-v0.3.2-complete.zip.sha256` 并核验；**Code → Download ZIP** 是可变的 `main` 源码快照，不等于固定完整包。
- 相关论文稿尚未经过同行评审。OpenAI Codex 仅辅助工程；科学判断与发布责任由 Xiao Chen 承担，OpenAI 不作为科学认证方或机构背书方。
