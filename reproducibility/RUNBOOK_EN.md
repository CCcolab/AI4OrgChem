# Reproducing the GitHub curated release

This runbook covers only content that can be executed independently from the curated GitHub release. It does not assume access to development logs, monograph full text, historical programs, raw quantum-chemistry outputs, or private API credentials.

## Canonical platform

The canonical scientific runtime is **WSL 2 / Ubuntu 24.04**. Native Windows can inspect Markdown and JSON and run the result-integrity validator, but it is not certified as equivalent to the validated PySCF, MACE/NequIP CUDA, or PySR runtime. See `PLATFORM_MATRIX_EN.md`.

## 1. Verify frozen evidence

From the repository root:

```bash
bash reproducibility/wsl/ai4orgchem-verify
python software/scripts/validate_evidence_navigation.py
python software/scripts/validate_wsl_release.py
python software/scripts/validate_release_package.py
```

The checks validate packaged P01-P14 results, bilingual evidence navigation, and WSL release boundaries. They do not rerun expensive quantum chemistry.

## 2. Create the isolated public review environment

Enter the installed distribution from PowerShell:

```powershell
wsl -d Ubuntu-24.04
```

Inspect existing environments before any creation command:

```bash
micromamba env list
```

If `ai4orgchem-public` is absent, create it explicitly. Do not overwrite or force-update an existing environment.

```bash
micromamba create -f reproducibility/environment.yml
source reproducibility/wsl/activate-ai4orgchem-public.sh
```

Install and test the public core:

```bash
cd software
python -m pip install -e ".[science,test]"
python -m pytest -p no:cacheprovider
```

CPU execution is sufficient for the focused tests. Full historical calculations and GPU training environments are outside the first curated release commitment.

## 3. Supported layouts and boundaries

- The Shell entry points auto-detect a GitHub clone and also support `/opt/ai4orgchem/publication` deployments.
- `environment.yml` is a minimal CPU review environment, not a machine image.
- Historical MACE and NequIP runs used isolated environments with incompatible `e3nn` requirements; those GPU environments are not silently reconstructed here.
- Monograph files, copyrighted full text, private paths, caches, model weights, and credentials are excluded.
