# Selected public software

[中文目录说明](README.md) (Chinese)

This directory contains independently implemented LFMO and conditional-SCF core code, directly related tests, and self-contained public validation entry points. Internal orchestration, logs, caches, and scripts dependent on an unpublished development tree are excluded. The monograph's program code is not included.

## Contents

- `src/ai4orgchem/lfmo/`: nonorthogonal subspaces, reflection adapters, state masks, KOST, and GL helpers.
- `src/ai4orgchem/qm/`: AO classification, ERI masks, conditional SCF, and independent energy assembly.
- `tests/`: 69 focused tests associated with public modules, including five P14 evidence-eligibility regression tests.
- `scripts/validate_public_evidence.py`: checks packaged P01–P14 machine results and frozen determinations.
- `scripts/validate_p14_evidence.py`: rebuilds P14 gates from lower-level published JSON and checks schema, duplicate keys, references, hashes, and coordinates; it does not rerun expensive QM.
- `scripts/validate_evidence_navigation.py`: checks bilingual fourteen-item navigation and its evidence contracts.
- `scripts/validate_wsl_release.py`: checks WSL deployment modes and platform boundaries.
- `scripts/validate_release_package.py`: checks syntax, Markdown links, SHA manifest, sensitive data, paths, file sizes, and duplicate files.
- `scripts/refresh_release_snapshot.py`: regenerates the inventory and SHA-256 snapshot after authorized changes.
- `scripts/run_p14_*.py` and `scripts/classify_p14_strained_aromatic_pi_distortivity.py`: P14 calculation entry points and deterministic eligibility classifier; costly runs write to an ignored reproduction directory.

From the repository root, run:

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```

See the [English runbook](../reproducibility/RUNBOOK_EN.md) for installation and testing. WSL 2 / Ubuntu 24.04 is the authoritative scientific runtime; native Windows has narrower verification scope. The selected public package does not promise reproduction of every expensive historical calculation from a single clone.
