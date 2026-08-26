# Independent Computational Tests of Counter-Traditional Propositions in Organic Chemistry

## Subtitle

Fourteen reproducible LFMO and energy-based assessments

**Author:** Xiao Chen

**Correspondence:** chenxiao0101@gmail.com

## Abstract

**Scientific source under assessment:** Zhong-Heng Yu, *Questioning Fundamental Principles of Organic Chemistry* (2024).

Conjugative stabilization, conjugation-driven planarization, and steric destabilization are widely used as organizing heuristics in organic chemistry. *Questioning Fundamental Principles of Organic Chemistry* proposed a set of counter-traditional claims, but its specialized localized-state constructions, historical coordinates, and software were not fully public. Without using the monograph's code, we translated fourteen major propositions into falsifiable computational tasks and independently reconstructed them from published equations, tables, numerical anchors, and frozen source-proxy protocols. The workflow covered localized fragment molecular-orbital states, conditional SCF, pi/sigma classification, DSI/FUD/GL/PLG energy ledgers, direct-interaction/orbital-response analysis, relaxed potential-energy scans, and virtual-reference aromatic energies. All propositions received determinate classifications: twelve were consistent or scope-consistent with the monograph, two were partially consistent, and none was globally inconsistent. Representative results include destabilizing LFMO pi-pi endpoints at all eleven technically valid tested points, a GL-defined butadiene conjugation energy of +1.575676 kcal/mol, a cyclobutadiene ADE of +53.822467 kcal/mol, a benzene ESE of -37.412764 kcal/mol, and a strained-aromatic C12H6 endpoint of 67.086899 kcal/mol. The partially consistent cases retain an opposite-sign inductive component for substituted benzene and a cross-estimator disagreement in the exact annulene size onset. The evidence supports the monograph's methodological criticism that textbook heuristics should not be promoted to universally sufficient mechanistic explanations. It neither establishes that traditional organic chemistry is globally incorrect nor introduces a universal opposite law of conjugative destabilization. The subsequent AI4S engineering line completed bounded data qualification, MACE/NequIP family holdouts, active-learning label return, PySR blind tests, and a read-only evidence agent. These results test engineering feasibility without replacing the quantum-chemical evidence.

## 1. Introduction

Chemical heuristics compress difficult electronic-structure problems into useful expectations. Their explanatory status becomes problematic, however, when a common trend is treated as an unconditional causal law. We examine three computational questions: whether electronic interaction must planarize conjugated frameworks; whether pi-pi, pi-sigma, and nonbonded sigma-sigma conditional-state endpoints must carry their textbook signs; and whether conjugation and aromatic energies require empirical thermochemical references. Historical identity reproduction, source-aligned reconstruction, and cross-method trend evidence were kept separate, and negative or partially consistent outcomes were retained.

## 2. Methods overview

Each proposition was preregistered operationally by freezing the molecular system, geometry, electronic-structure level, state definition, sign convention, and completion rule. PySCF supported the independent quantum-chemical implementation, while RDKit was used for graph and formula checks and published numerical ledgers were independently recomputed. LFMO tasks used state-specific occupied spaces, conditional SCF, and pi/sigma subspace classification. Aromaticity tasks used published operational definitions including GL, GE, VDE, ADE, ESE, LDE, and PLG. Each proposition is connected to a protocol, processed evidence, report, and validator. AI tools assisted engineering and organization but did not assign scientific signs or replace quantum-chemical evidence.

## 3. Results

The complete classifications and boundaries are given in the accompanying evidence matrix. P04-P07 show that, within the tested source-proxy domain, the two-term narrative of conjugative stabilization versus steric destabilization is insufficient to describe LFMO conditional-state endpoints and structural response. P08 shows that the butadiene conclusion depends on an explicit GL operational definition and that selective hydrogenation references do not provide a unique sign. P09-P10 reconstruct aromatic-energy magnitudes and expose opposing electronic and nuclear-repulsion contributions along a benzene bond-alternation coordinate. P11-P12 are partially consistent and identify concrete limits of two subclaims. P13-P14 support the tested polycyclic-benzenoid rule hierarchy and pi-distortivity in the frozen C12H6 system.

## 4. Discussion

The combination of twelve consistent and two partially consistent outcomes is more informative than a single claim of successful reproduction. Several counter-traditional propositions survive independent implementation, while their dependence on state definitions, source-proxy geometries, and estimators remains explicit. The strongest aggregate conclusion is not that classical theory is wrong, but that textbook heuristics do not automatically acquire mechanistic authority outside their empirical domain. Interaction, orbital response, and geometric relaxation must be evaluated under explicit state contracts.

## 5. Limitations

Some historical Cartesian coordinates and the original software were unavailable; several results are source-proxy rather than historical-identity reproductions. Targets with different state contracts must not be summed across protocols. Phase 5 completed three-family holdout baselines, with pi-pi macro-average errors of 108.0 and 108.2 meV/atom for MACE and NequIP, respectively; this scale remains insufficient for industrial or universal generalization claims. Post-return active-learning effects were mixed, and only the pi-pi PySR candidate passed the bounded blind test. The AI results therefore establish engineering feasibility rather than replacing the P01-P14 quantum-chemical evidence.

## 6. Conclusions

We provide an independent, reproducible, and scope-bounded computational assessment of fourteen counter-traditional propositions in organic structure theory. The aggregate evidence supports criticism of the unconditional generalization of several textbook principles while preserving explicit exceptions and methodological boundaries. The accompanying AI4S workflow demonstrates an operational chain from frozen evidence to bounded learning, active sampling, symbolic testing, and traceable explanation, while retaining its small-sample errors and failed tests.

## Data and code availability

Project-authored code and documentation are licensed under Apache-2.0. The `v0.1.0` release includes versioned core code, machine-readable processed evidence, frozen protocols, reports, tests, a self-contained evidence validator, and environment documentation. The monograph and third-party materials are not relicensed by the project.

## Author contributions

Xiao Chen: Conceptualization; Methodology; Software; Validation; Investigation; Data Curation; Writing; Visualization; Project Administration.

## Competing interests

The author declares no financial or non-financial competing interests.
