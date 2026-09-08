# Rapid Review Guide for Quantum-Chemistry Experts

[中文版](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS_zh-CN.md)

This guide is for readers who know quantum chemistry but do not need prior experience with GitHub, artificial intelligence, or software engineering. It lets an expert understand the project in **10 minutes**, audit one proposition in **30 minutes**, and run machine-consistency checks only if desired.

**Scientific source under review:** Zhong-Heng Yu's monograph, *Questioning Fundamental Principles of Organic Chemistry* (2024).

> AI4OrgChem is an independent computational reconstruction and evidence-assessment project, not an institutional certification or an AI vote on scientific truth. AI supports protocol management, evidence tracing, and engineering. Energy signs, numerical results, and classifications come from explicit quantum-chemical definitions and frozen computational evidence.

> **Current stable review object:** [`v0.3.0`](https://github.com/CCcolab/AI4OrgChem/releases/tag/v0.3.0). GitHub's **Code → Download ZIP** is a mutable snapshot of the current `main` branch. For reproducible scientific review or citation, use the complete Release package and verify its published SHA-256.

## 1. Read the repository as a paper with expandable supporting information

You do not need to start with source code. The scientific argument has five layers:

```text
Proposition from the monograph
  ↓ translated into a falsifiable question
data-card.md: system, geometry, source identity, and missing information
  ↓
protocol.md: system, states, method, sign convention, and decision rule
  ↓
result.json / result.jsonl: machine-readable values and classification fields
  ↓
report.md: interpretation, agreement or disagreement, and scope limits
  ↓
evidence matrix and validators: cross-check all fourteen propositions and file integrity
```

Each file has a distinct evidentiary responsibility:

| File | Question to ask | What it does not establish |
|---|---|---|
| `data-card.md` | What molecule, geometry, source, and missing information are involved? | It does not provide the final physical interpretation. |
| `protocol.md` | When were the energy difference, states, method, sign, and criterion frozen? Which parts were prospectively preregistered and which were frozen after historical reconstruction? | It must not redefine the test after seeing the answer or equate release-time freezing with prospective preregistration. |
| `result.json` / `result.jsonl` | Are the values, units, protocol ID, and classification fields machine-readable? | It does not replace chemical interpretation. |
| `report.md` | Which part of the proposition is supported, and within what limits? | It must not turn one tested system into a universal law. |
| Validators | Are values, classifications, links, and hashes internally consistent? | They do not rerun expensive electronic-structure calculations. |

## 2. The 10-minute route

### Step 1 — Spend two minutes identifying the actual claim

Read “Scientific assessment” and “Reproducibility and evidence boundaries” on the [English home page](README.md). Retain three statements:

1. Of fourteen propositions, twelve are consistent or scope-consistent, two are partially consistent, none is globally inconsistent, and none is unknown. Post-release review temporarily lowered P14, after which a qualified production optimization passed every registered gate and restored it to consistent.
2. The evidence supports a bounded methodological criticism: several textbook heuristics do not automatically become universally sufficient mechanistic explanations.
3. The project does not claim that traditional organic chemistry is globally wrong and does not propose a reverse universal law that conjugation must always be destabilizing.

### Step 2 — Spend three minutes checking that different claims remain separate

Open the [P01–P14 evidence matrix](manuscripts/P01-P14_evidence_matrix_zh-CN.md). Its rows separate:

```text
textbook heuristic → testable monograph proposition → independent method
→ project classification → scope and boundary
```

The final column matters more than the word “consistent.” A result obtained for a source-proxy geometry, a particular state contract, or one operational energy definition must remain limited to that domain.

### Step 3 — Spend five minutes auditing one representative proposition

| Question | Recommended entry | Why it is useful first |
|---|---|---|
| Can an LFMO pi–pi endpoint have a destabilizing sign? | [P04](evidence/P01-P14/P04/report.md) | It directly tests the conjugation-energy sign at eleven technically valid endpoints. |
| Why is the butadiene conjugation energy positive? | [P08](evidence/P01-P14/P08/report.md) | It exposes the GL definition, reference construction, and `+1.575676 kcal/mol` result. |
| Can aromatic and antiaromatic energies be constructed theoretically? | [P09](evidence/P01-P14/P09/report.md) | It permits a direct sign and magnitude check for benzene and cyclobutadiene. |
| How does the project handle incomplete support? | [P11](evidence/P01-P14/P11/substituent-report.md) or [P12](evidence/P01-P14/P12/report.md) | These preserve an opposite-sign component and a cross-estimator onset difference. |

For one proposition, read the files in this order:

1. `data-card.md`: identify the system, geometry provenance, method level, and unavailable information;
2. `protocol.md`: inspect the estimand, endpoint states, energy difference, and sign convention;
3. `result.json` or `result.jsonl`: follow the proposition-specific schema or validator to locate the numerical value, unit, protocol identity, and scoped classification; field names and nesting differ across historical result formats;
4. `report.md`: verify that the interpretation quotes the machine result faithfully and preserves its boundaries.

If interpretation precedes definition, or if the sign convention is ambiguous, the evidence grade should be reduced. The repository is designed to make such defects visible.

## 3. The 30-minute single-proposition audit

Use these six questions for any P01–P14 item. A proposition is scope-complete only when all six have explicit answers.

| Audit question | Where to find the answer |
|---|---|
| 1. What falsifiable proposition from the monograph is tested? | Evidence index and `protocol.md` |
| 2. Are molecule, geometry, electronic state, method, and basis fixed? | `data-card.md` and `protocol.md` |
| 3. What are the endpoint states, and what does the sign mean? | Definitions and sign convention in `protocol.md` |
| 4. Do all values belong to one protocol, without summing incompatible state contracts? | `protocol_id`, state fields, and `report.md` |
| 5. Is the result numerically consistent, opposite in sign, or only trend-consistent with the monograph? | `report.md` and evidence matrix |
| 6. Are source-proxy reconstruction, historical-identity reproduction, and cross-method support distinguished? | Boundary sections of `data-card.md` and `report.md` |

Three common misreadings deserve special attention:

- **A positive energy does not establish a universal law of destabilization.** It applies to the stated energy definition, endpoint states, and tested systems.
- **Variational lowering is not identical to stabilization by a particular orbital interaction.** Direct interaction, orbital response, and final endpoint must be interpreted separately under the protocol.
- **Pi–pi, pi–sigma, and sigma–sigma values from different protocols cannot be added at will.** Closure is meaningful only under a common state contract and total-energy functional.

Evidence must also be read on two separate axes. `R1–R3` records scientific evidence level, whereas `replay_status` and `M1/M2` record Agent replay maturity. Here `M2-scoped` means only that an external model selected one registered whitelist replay plan that a local orchestrator executed in a clean bundle-only environment; the full external model session and a generally replayable runtime are not public. This improves bounded reproducibility but does not raise R1–R3. Cross-version evidence must also be marked `SAME_ESTIMAND`, `COMPLEMENTARY`, or `INCOMPARABLE`; only same-estimand results can directly raise the numerical reproduction level of the original proposition.

## 4. Understand the fourteen results without being distracted by AI

| Scientific question | Propositions | Primary concern |
|---|---|---|
| Orbital representation versus electron density | P01 | Whether orbital localization changes the density or RHF energy |
| Conjugation, twisting, and conditional sigma/pi states | P02–P07 | Geometry response, pi–pi, pi–sigma, nonbonded sigma–sigma, and orbital response |
| Butadiene and theoretical aromatic energies | P08–P10 | GL/virtual references, benzene/cyclobutadiene, electronic energy versus nuclear repulsion |
| Boundaries and exceptions in aromaticity | P11–P12 | Furan, substituent decomposition, and annulene size onset |
| Polycyclic and strained aromatic systems | P13–P14 | GL rule hierarchy, graph enumeration, and pi-driven distortion |

Machine learning and the evidence agent form a separate engineering layer. MACE, NequIP, active learning, and PySR ask whether frozen evidence is learnable in a bounded setting or can generate testable candidate relations. They cannot change any P01–P14 quantum-chemical classification. A scientific reviewer may initially skip the entire [`ai4s-agent/`](ai4s-agent/README.md) directory.

### `v0.3.0` adds enhancement evidence, not a reclassification of the fourteen propositions

| Enhancement task | Review entry supplied by `v0.3.0` | Relation to P01–P14 |
|---|---|---|
| WP1 | Cyclobutadiene multireference anchor | Supports the tested sign while retaining substantial method sensitivity |
| WP2 | 8/8 PySCF/Psi4/NWChem anchors and 2/2 relative-energy pairs | Improves ordinary-state cross-program reproduction without rewriting the classifications |
| WP3 | Benzene D6h symmetry-adapted modes and constrained electronic intervention | Gives P10-B its own mechanism evidence without automatically upgrading P10-A |
| WP4-A | Source-aligned CESE lane | Preserves the monograph-aligned estimand identity |
| WP4-B | Six-point paired physical-state 0 K ASE pilot | Remains a different estimand from WP4-A; the two are neither averaged nor substituted |
| WP5 | External clean Agent replay | Reaches M2-scoped maturity for one whitelisted replay; it does not expose the full external-model session or automatically raise R1–R3 |
| WP6 | Fixed tag, complete archive, hashes, CI, and post-tag clean verification | Fixes publication identity without generating a new scientific sign |

See the [`v0.3.0` scientific-closure entry](science-v0.3/README.md) and the [post-release erratum](project/V0.3.0_POST_RELEASE_ERRATUM_2026-09-08.md). The immutable release added evidence; current `main` corrects P14 evidence eligibility, publishes a qualified production optimization, and reports twelve consistent/scope-consistent plus two partially consistent propositions.

## 5. Examine the two “partially consistent” results and the P14 correction first

A credible independent assessment must retain results that do not fully support the source claim.

### P11 — Opposite sign for the substituted-benzene inductive component

- The furan LDE result is consistent with the monograph.
- The cyanobenzene conjugative component is `+1.180928 kcal/mol`, close to the monograph's approximately `+1.2 kcal/mol`.
- Two frozen inductive diagnostic routes give `-0.335714` and `-0.580151 kcal/mol`, whereas the monograph reports `+0.49 kcal/mol`; they are not described as fully independent software or data sources.
- Because the complete historical Cartesian coordinates are unavailable, the project classifies P11 as partially consistent rather than claiming a direct refutation of the historical calculation.

### P12 — Same large-annulene trend, different numerical onset

- The source-aligned CESE ledger in the monograph describes onset near `N=16/18`.
- A 2025 external study reports an energy boundary around `N>30` under a different ASE estimator; this is literature support, not same-estimand reproduction of the CESE threshold.
- AI4OrgChem `v0.3.0` WP4-B separately evaluates the paired `8/10`, `16/18`, and `32/34` physical-state 0 K ASE pilot, while remaining isolated from the WP4-A source-aligned CESE lane.
- The lanes may be compared for the qualitative tendency toward polyene-like behavior, but neither the six-point pilot nor cross-estimator onset values establish a universal annulene-size law.

### P14 — Review-detected eligibility defect corrected by qualified production evidence

- The repaired classifier rejects the old STO-3G technical pilot because it disables scientific classification and exceeds the gradient threshold.
- New B3LYPG/6-31G(d) G/PLG production optimizations have maximum gradients `0.00146286/0.00116557 Eh/Å`, no active bounds, and pass all registered method, protocol, SCF, electron-count and numerical gates.
- They give `dΔr=0.172204 Å` versus the source `0.179 Å` and an optimized endpoint of `+67.679719 kcal/mol` versus `+67.08 kcal/mol`; both residuals pass the preregistered tolerances.
- P14 is therefore restored to consistent, but only for one C12H6 planar-D3h five-parameter source-proxy system; no full-Cartesian frequency, wider-symmetry, nineteen-molecule, or universal-law claim is made.

P11 and P12 remain the direct test that unfavorable and incomparable evidence is preserved. P14 additionally demonstrates that a review-detected eligibility defect is not hidden: it was first downgraded, then restored only after qualified replacement evidence passed the repaired gate.

## 6. Credibility checks that require no programming

Without running a command, a reviewer can:

1. select three entries in the [English evidence index](evidence/P01-P14/README.md) and confirm that each has a data card, protocol, machine result, and report;
2. compare the sign definition in `protocol.md` with every use of “stabilizing” or “destabilizing” in `report.md`;
3. confirm that P11 and P12 retain the opposite sign and estimator difference, and that P14 preserves the missing-coordinate/D3h limitations while exposing the rejected pilot and qualified replacement optimization;
4. verify that a source-proxy result is never presented as complete historical-identity reproduction;
5. verify that AI predictions are never allowed to rewrite a quantum-chemical classification.

Failure of any one check is sufficient reason to reject the corresponding strong claim.

## 7. Optional: five copy-and-paste consistency checks

These commands do not rerun expensive quantum chemistry. Until `v0.3.1` is released, clone or download current `main` and read the post-release erratum; the immutable `v0.3.0` package predates this correction. Enter the root containing `README.md` and `software/`. With Python 3.12, run:

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
python science-v0.3/scripts/science_v0.3/validate_github_v03_release.py --project . --package science-v0.3
```

Expected output includes:

- `status: PASS`;
- `propositions_checked: 14`;
- `propositions_navigated: 14`;
- twelve consistent or scope-consistent, two partially consistent, zero globally inconsistent, and zero unknown classifications.
- `WP6_V03_RELEASE_VALIDATION_OK`.

Readers interested only in scientific evidence do not need PySCF, CUDA, MACE, or PySR. Full runtime and WSL 2 information is provided only for software and platform reproduction in the [reproducibility directory](reproducibility/README.md).

## 8. Recommended review wording

For a reviewer who has not independently rerun every historical computation, the strongest defensible summary is:

> AI4OrgChem conducted a layered, auditable evidence assessment of fourteen counter-traditional propositions in organic structure theory and independently reconstructed the computationally testable propositions without using the monograph's program code, under explicitly frozen systems, state definitions, energy differences, and source-proxy boundaries. Current public evidence is consistent or scope-consistent with twelve propositions and partially consistent with two. Post-release review exposed a P14 evidence-eligibility defect; the project rejected the old technical pilot, repaired the gate, and restored P14 only after a B3LYPG/6-31G(d) production optimization passed every registered criterion. The aggregate result supports criticism of unconditionally universalizing several classical heuristics, but it does not reject traditional organic chemistry as a whole or establish a universal law in the opposite direction. The release has not undergone peer review.

## 9. Shortest navigation path

- [English home page](README.md)
- [`v0.3.0` stable release and official download](https://github.com/CCcolab/AI4OrgChem/releases/tag/v0.3.0)
- [P01–P14 evidence index](evidence/P01-P14/README.md)
- [Evidence matrix](manuscripts/P01-P14_evidence_matrix_zh-CN.md)
- [Publication positioning](manuscripts/PUBLICATION_POSITIONING_EN.md)
- [Reproducibility and platform boundaries](reproducibility/README.md)
- [Authorship, contributions, and competing interests](AUTHORS.md)
