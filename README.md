# AI4OrgChem

[![Validation](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml/badge.svg)](https://github.com/CCcolab/AI4OrgChem/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/CCcolab/AI4OrgChem)](LICENSE)
[![Evidence](https://img.shields.io/badge/evidence-P01--P14%20internally%20checked-2ea44f)](evidence/P01-P14/README.md)
[![WSL2](https://img.shields.io/badge/WSL2-Ubuntu%2024.04%20verified-0078D4)](reproducibility/wsl/README.md)
[![AI assistance](https://img.shields.io/badge/AI%20assistance-OpenAI%20Codex%20GPT--5.6-6f42c1)](AUTHORS.md)

[中文说明](README_zh-CN.md)

AI4OrgChem is an **AI for Science (AI4S) Agent** for independent computational reconstruction and evidence assessment of counter-traditional propositions in organic structure theory. The project was motivated by Zhong-Heng Yu's monograph, ***Questioning Fundamental Principles of Organic Chemistry*** (2024), and was implemented without using the monograph's program code.

> **AI-assisted research and engineering:** **OpenAI Codex (GPT-5.6)**. Project authorship, scientific decisions, interpretations, and publication responsibility remain with Xiao Chen; OpenAI is not presented as a project author, scientific certifier, peer reviewer, or institutional endorser.

The associated manuscript has not yet undergone peer review. Detailed classifications, qualifications, and corrections are recorded in the [evidence matrix](manuscripts/P01-P14_evidence_matrix_EN.md) and linked proposition records.

## Why this project exists

Textbook ideas such as conjugative stabilization, conjugation-driven planarization, steric destabilization, and aromatic stabilization are useful chemical heuristics. Problems arise when a heuristic is promoted to an unconditional mechanistic law. AI4OrgChem converts fourteen major propositions into falsifiable computational tasks with frozen systems, state definitions, sign conventions, numerical outputs, and explicit scope boundaries.

The project asks how far independent calculations and other traceable evidence support each proposition within a defined molecular and methodological scope, and where the evidence remains incomplete.

## Independent method

- Define the molecule, geometry, electronic state, Hamiltonian, comparison quantity, sign convention, and decision boundary before evaluating a claim.
- Independently implement orbital localization, conditional electronic-structure calculations, geometry or energy scans, and energy decomposition where the proposition permits them; the monograph's program code is not used.
- Keep quantum-chemical calculations, published-value reanalysis, graph checks, and literature evidence distinct. A proposition-level assessment is not a claim that all fourteen items received equal-status quantum-chemical reproduction.
- Use the AI4S Agent for protocol management, evidence tracing, bounded molecular learning, active sampling, symbolic testing, and source-aware explanation. Model predictions do not replace electronic-structure results or determine scientific signs.

## Scientific outcome

The project has assembled protocols, processed results, data cards, and scope-limited reports for fourteen propositions. It also publishes the software and validation paths needed to inspect these records. The [evidence collection](evidence/P01-P14/README.md) and [matrix](manuscripts/P01-P14_evidence_matrix_EN.md) provide the proposition-level findings and their limitations.

Representative frozen results are:

| Result | Value or classification |
|---|---:|
| Technically valid LFMO pi-pi endpoints | 11/11 in the destabilizing direction |
| GL-defined butadiene conjugation energy | +1.575676 kcal/mol |
| Cyclobutadiene ADE | +53.822467 kcal/mol |
| Benzene ESE | -37.412764 kcal/mol (monograph: -36.3; absolute difference 1.112764, about 3.07%) |
| Strained-aromatic C12H6 endpoints | +67.086899 kcal/mol fixed-geometry source-level anchor; +67.679719 kcal/mol qualified production optimization (`dDelta-r=0.172204 A`) |

These results support a bounded methodological conclusion: several textbook heuristics do not automatically provide universally sufficient mechanistic explanations. They do **not** establish that traditional organic chemistry is globally wrong, do not create a universal opposite law of conjugative destabilization, and do not constitute institutional certification of the monograph.

The fourteen propositions form a layered, auditable evidence chain rather than fourteen equal-status quantum-chemistry reproductions. Independent QM, source-aligned/source-proxy reconstruction, published-value reanalysis, and graph/literature evidence retain distinct identities.

Additional work includes a same-Hamiltonian path audit, state-specific planar recalculations, and an evidence-eligibility gate for the strained-aromatic endpoint. Their exact claims and superseded records remain in the proposition reports.

Readers in quantum chemistry, computational chemistry, or organic-structure theory can begin with the [AI4S Rapid Reproduction and Evidence Verification Guide](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md): understand the overall argument in 10 minutes and verify any single proposition in 30 minutes without reading code first.

## Community review

Independent reproduction, falsification, and scoped scientific disagreement are welcome. Use the repository's structured issue forms to submit an [independent reproduction](https://github.com/CCcolab/AI4OrgChem/issues/new?template=independent-reproduction.yml), [scientific disagreement](https://github.com/CCcolab/AI4OrgChem/issues/new?template=scientific-disagreement.yml), [documentation correction](https://github.com/CCcolab/AI4OrgChem/issues/new?template=documentation-correction.yml), or [new molecular test proposal](https://github.com/CCcolab/AI4OrgChem/issues/new?template=new-molecular-test.yml).

## AI4S Agent engineering

The completed bounded engineering line connects frozen scientific evidence to machine-readable data, equivariant learning, active-learning return, symbolic discovery, and a read-only evidence agent.

- bounded dataset: 17 geometries, 3 molecular families, and 5 energy targets;
- pi-pi family-holdout macro RMSE: 108.0 meV/atom for MACE and 108.2 meV/atom for NequIP;
- active learning: acquisition succeeded, while post-return model effects were mixed;
- PySR: the bounded pi-pi blind test passed, while the pi-sigma test failed;
- evidence agent: answers are restricted to frozen evidence and must expose sources and scope.

The dataset is too small for industrial or universal molecular generalization. Details are provided in the [Agent capabilities and results](ai4s-agent/CAPABILITIES_AND_RESULTS_EN.md), [machine-readable evaluation summary](ai4s-agent/EVALUATION_SUMMARY.json), and [limitations](ai4s-agent/LIMITATIONS_EN.md).

## Repository map

| Path | Purpose |
|---|---|
| [`REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md`](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md) | Rapid AI4S reproduction and evidence-verification route for scientific readers |
| [`project/`](project/README_EN.md) | Background, research questions, value, achievements, and master proposition table |
| [`evidence/P01-P14/`](evidence/P01-P14/README.md) | Frozen data cards, protocols, processed results, and scoped reports |
| [`manuscripts/`](manuscripts/README_EN.md) | Evidence matrix and bilingual publication positioning; no pre-submission manuscript drafts are included |
| [`ai4s-agent/`](ai4s-agent/README_EN.md) | Agent architecture, capabilities, evaluation, governance, and limitations |
| [`software/`](software/README_EN.md) | Public LFMO/conditional-SCF implementation and 69 focused tests |
| [Typical reproduction programs](reproducibility/TYPICAL_PROGRAMS.md) | Select evidence checks, conditional-SCF tests, or downloadable QM reruns by cost, with step-by-step computation notes |
| [`reproducibility/`](reproducibility/README_EN.md) | Full runtime instructions, environments, and WSL 2 platform boundaries |
| [`figures/`](figures/README_EN.md) | Project-authored overview figure |
| [Science enhancement evidence (bilingual)](science-v0.2/README.md) | Self-contained configurations, selected results, decisions, reports, tests, and hashes |
| [Scientific-closure evidence (bilingual)](science-v0.3/README.md) | Seven-work-package extension and its separate evidence boundaries |
| [`manifests/`](manifests/README_EN.md) | File inventory and SHA-256 release manifest |

## Examine and reproduce

Start with the [rapid evidence-verification guide](REVIEW_GUIDE_FOR_QUANTUM_CHEMISTS.md) or [typical reproduction programs](reproducibility/TYPICAL_PROGRAMS.md). The [English runbook](reproducibility/RUNBOOK_EN.md) and [platform matrix](reproducibility/PLATFORM_MATRIX_EN.md) contain commands, hardware requirements, and the distinction between evidence checks and costly quantum-chemical reruns. For the longer Chinese-language computation guide, use the clearly labeled language switch at the top of this page.

## Reproducibility and evidence boundaries

- The original monograph, scans, publisher files, full-text extracts, and historical program code are not distributed here.
- Some historical Cartesian coordinates and software were unavailable; affected results are explicitly marked as source-proxy rather than identity reproductions.
- Targets with different state contracts must not be summed across protocols.
- AI model outputs are engineering evidence, not new quantum-chemical labels or independent proof of the scientific propositions.
- Models, private run directories, caches, API credentials, and copyrighted source materials are excluded from the public repository.

## Evidence matrix and publication positioning

- [Evidence matrix](manuscripts/P01-P14_evidence_matrix_EN.md)
- [Publication positioning](manuscripts/PUBLICATION_POSITIONING_EN.md)

## License

Project-authored software and documentation are released under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution and third-party boundaries. The license does not relicense the monograph or other third-party material.

## Citation

The sole project author is **Xiao Chen**. Contact: [chenxiao0101@gmail.com](mailto:chenxiao0101@gmail.com). AI-assisted research and engineering support was provided through **OpenAI Codex (GPT-5.6)**. Authorship, CRediT contributions, AI-assistance disclosure, and the competing-interests statement are recorded in the [bilingual authorship statement](AUTHORS.md). Machine-readable citation metadata is provided in [`CITATION.cff`](CITATION.cff). Affiliation and ORCID are omitted because they were not supplied.
