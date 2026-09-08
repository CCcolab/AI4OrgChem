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

1. Of fourteen propositions, twelve are consistent or scope-consistent, two are partially consistent, none is globally inconsistent, and none is unknown.
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
3. `result.json` or `result.jsonl`: locate `value`, `unit`, `protocol_id`, and `final_scoped_label`;
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

Evidence must also be read on two separate axes. `R1–R3` records scientific evidence level, whereas `replay_status` and `M1/M2` record Agent replay maturity. An M2 clean replay improves reproducibility but does not automatically raise R1–R3. Cross-version evidence must also be marked `SAME_ESTIMAND`, `COMPLEMENTARY`, or `INCOMPARABLE`; only same-estimand results can directly raise the numerical reproduction level of the original proposition.

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
| WP5 | External clean Agent replay | Reaches M2 engineering maturity without automatically raising R1–R3 |
| WP6 | Fixed tag, complete archive, hashes, CI, and post-tag clean verification | Fixes publication identity without generating a new scientific sign |

See the [`v0.3.0` scientific-closure entry](science-v0.3/README.md) for the complete status. The release adds evidence but leaves the twelve consistent/scope-consistent and two partially consistent P01–P14 classifications unchanged.

## 5. Examine the two “partially consistent” results first to test objectivity

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

These two propositions are the best test of whether the project preserves negative and ambiguous evidence rather than selecting only favorable results.

## 6. Credibility checks that require no programming

Without running a command, a reviewer can:

1. select three entries in the [English evidence index](evidence/P01-P14/README.md) and confirm that each has a data card, protocol, machine result, and report;
2. compare the sign definition in `protocol.md` with every use of “stabilizing” or “destabilizing” in `report.md`;
3. confirm that P11 and P12 retain the opposite sign, estimator difference, and missing-coordinate limitation;
4. verify that a source-proxy result is never presented as complete historical-identity reproduction;
5. verify that AI predictions are never allowed to rewrite a quantum-chemical classification.

Failure of any one check is sufficient reason to reject the corresponding strong claim.

## 7. Optional: five copy-and-paste consistency checks

These commands do not rerun expensive quantum chemistry. Download the complete package from the [`v0.3.0` Release](https://github.com/CCcolab/AI4OrgChem/releases/tag/v0.3.0), verify its SHA-256, extract it, open a terminal, and enter the root containing `README.md` and `software/`. With Python 3.12, run:

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

> AI4OrgChem conducted a layered, auditable evidence assessment of fourteen counter-traditional propositions in organic structure theory and independently reconstructed the computationally testable propositions without using the monograph's program code, under explicitly frozen systems, state definitions, energy differences, and source-proxy boundaries. The public evidence is consistent or scope-consistent with twelve propositions and partially consistent with two. `v0.3.0` adds multireference, three-program reproduction, mechanism intervention, dual-estimand, and clean Agent-replay evidence without changing those classifications. The aggregate result supports criticism of unconditionally universalizing several classical heuristics, but it does not reject traditional organic chemistry as a whole or establish a universal law in the opposite direction. The release has not undergone peer review.

## 9. Shortest navigation path

- [English home page](README.md)
- [`v0.3.0` stable release and official download](https://github.com/CCcolab/AI4OrgChem/releases/tag/v0.3.0)
- [P01–P14 evidence index](evidence/P01-P14/README.md)
- [Evidence matrix](manuscripts/P01-P14_evidence_matrix_zh-CN.md)
- [Publication positioning](manuscripts/PUBLICATION_POSITIONING_EN.md)
- [Reproducibility and platform boundaries](reproducibility/README.md)
- [Authorship, contributions, and competing interests](AUTHORS.md)
