# AI4OrgChem

[中文说明](README_zh-CN.md)

AI4OrgChem is an **AI for Science (AI4S) Agent** for independent computational reconstruction and evidence assessment of counter-traditional propositions in organic structure theory. The project was motivated by *Questioning Fundamental Principles of Organic Chemistry* and was implemented without using the monograph's program code.

> **Release status:** local `v0.1.0-rc1` candidate. The repository has not yet been published or peer reviewed.

## Why this project exists

Textbook ideas such as conjugative stabilization, conjugation-driven planarization, steric destabilization, and aromatic stabilization are useful chemical heuristics. Problems arise when a heuristic is promoted to an unconditional mechanistic law. AI4OrgChem converts fourteen major propositions into falsifiable computational tasks with frozen systems, state definitions, sign conventions, numerical outputs, and explicit scope boundaries.

The project asks whether independently reconstructed quantum-chemical evidence supports, contradicts, or only partially supports each proposition. AI assists protocol management, evidence tracing, bounded molecular learning, active sampling, symbolic testing, and explanation; it does not assign scientific signs or replace electronic-structure calculations.

## Scientific outcome

All fourteen propositions received determinate classifications within their declared tested domains:

- **12 consistent or scope-consistent** with the corresponding monograph proposition;
- **2 partially consistent**: P11 retains an opposite-sign inductive component, and P12 retains a cross-estimator disagreement in the exact annulene onset;
- **0 globally inconsistent and 0 unknown**.

Representative frozen results are:

| Result | Value or classification |
|---|---:|
| Technically valid LFMO pi-pi endpoints | 11/11 in the destabilizing direction |
| GL-defined butadiene conjugation energy | +1.575676 kcal/mol |
| Cyclobutadiene ADE | +53.822467 kcal/mol |
| Benzene ESE | -37.412764 kcal/mol |
| Strained-aromatic C12H6 endpoint | +67.086899 kcal/mol |

These results support a bounded methodological conclusion: several textbook heuristics do not automatically provide universally sufficient mechanistic explanations. They do **not** establish that traditional organic chemistry is globally wrong, do not create a universal opposite law of conjugative destabilization, and do not constitute institutional certification of the monograph.

See the [P01-P14 evidence matrix](manuscripts/P01-P14_evidence_matrix_zh-CN.md) and the [evidence collection](evidence/P01-P14/README.md).

## AI4S Agent engineering

The completed bounded engineering line connects frozen scientific evidence to machine-readable data, equivariant learning, active-learning return, symbolic discovery, and a read-only evidence agent.

- bounded dataset: 17 geometries, 3 molecular families, and 5 energy targets;
- pi-pi family-holdout macro RMSE: 108.0 meV/atom for MACE and 108.2 meV/atom for NequIP;
- active learning: acquisition succeeded, while post-return model effects were mixed;
- PySR: the bounded pi-pi blind test passed, while the pi-sigma test failed;
- evidence agent: answers are restricted to frozen evidence and must expose sources and scope.

The dataset is too small for industrial or universal molecular generalization. Details are provided in the [Agent capabilities and results](ai4s-agent/CAPABILITIES_AND_RESULTS_zh-CN.md), [machine-readable evaluation summary](ai4s-agent/EVALUATION_SUMMARY.json), and [limitations](ai4s-agent/LIMITATIONS_zh-CN.md).

## Repository map

| Path | Purpose |
|---|---|
| [`project/`](project/README.md) | Background, research questions, value, achievements, and master proposition table |
| [`evidence/P01-P14/`](evidence/P01-P14/README.md) | Frozen data cards, protocols, processed results, and scoped reports |
| [`manuscripts/`](manuscripts/README.md) | English and Chinese manuscripts, evidence matrix, and publication positioning |
| [`ai4s-agent/`](ai4s-agent/README.md) | Agent architecture, capabilities, evaluation, governance, and limitations |
| [`software/`](software/README.md) | Public LFMO/conditional-SCF implementation and 64 focused tests |
| [`reproducibility/`](reproducibility/README.md) | Runtime instructions and WSL 2 platform boundaries |
| [`figures/`](figures/README.md) | Project-authored overview figure |
| [`manifests/`](manifests/FILE_INVENTORY.md) | File inventory and SHA-256 release manifest |

## Quick verification

Validate the packaged P01-P14 result integrity without rerunning expensive quantum chemistry:

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```

Expected output includes `"status": "PASS"`, `"propositions_checked": 14`, and `"propositions_navigated": 14`.

Install and run the public core tests:

```bash
cd software
python -m pip install -e ".[science,test]"
python -m pytest -p no:cacheprovider
```

The canonical scientific runtime is **WSL 2 / Ubuntu 24.04**. Native Windows is supported only for limited evidence inspection and is not claimed to be equivalent to the validated PySCF, MACE/NequIP CUDA, or PySR runtime. See the [runtime platform matrix](reproducibility/PLATFORM_MATRIX_EN.md), [English runbook](reproducibility/RUNBOOK_EN.md), and [portable WSL entry points](reproducibility/wsl/README.md).

## Reproducibility and evidence boundaries

- The original monograph, scans, publisher files, full-text extracts, and historical program code are not distributed here.
- Some historical Cartesian coordinates and software were unavailable; affected results are explicitly marked as source-proxy rather than identity reproductions.
- Targets with different state contracts must not be summed across protocols.
- AI model outputs are engineering evidence, not new quantum-chemical labels or independent proof of the scientific propositions.
- Models, private run directories, caches, API credentials, and copyrighted source materials are excluded from this release candidate.

## Manuscripts

- [English manuscript](manuscripts/MANUSCRIPT_EN.md)
- [Chinese manuscript](manuscripts/MANUSCRIPT_zh-CN.md)
- [Publication positioning](manuscripts/PUBLICATION_POSITIONING_EN.md)

## License

Project-authored software and documentation are released under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution and third-party boundaries. The license does not relicense the monograph or other third-party material.

## Citation

The release author is **Xiao Chen**. Machine-readable citation metadata is provided in [`CITATION.cff`](CITATION.cff). Affiliation and ORCID are intentionally omitted until explicitly supplied.
