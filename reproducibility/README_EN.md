# Public reproduction routes

[中文目录说明](README.md) (Chinese)

Choose the level of work before running anything:

- [Typical reproduction programs](TYPICAL_PROGRAMS.md): choose evidence checks, conditional-SCF tests, or costly QM reruns by input, output, cost, and scientific boundary.
- [English runbook](RUNBOOK_EN.md): commands for frozen-evidence validation and public software tests.
- [English platform matrix](PLATFORM_MATRIX_EN.md): authoritative WSL 2 environment versus the narrower native-Windows and isolated GPU paths.

The extended Chinese-language computation guide is available through the clearly labeled language switch above.

The minimal CPU environment is declared in `environment.yml`. `conda-linux-64.explicit.txt` records a 2026-08-12 Conda-layer snapshot of the authoritative WSL scientific environment; it is not a full lock of later GPU or pip environments. The [WSL launcher instructions](wsl/README.md) are bilingual and support both a GitHub clone and an `/opt/ai4orgchem/publication` deployment.

The public package supports checking processed evidence and testing selected code. It does not treat native Windows, a developer-machine image, GPU caches, or private run directories as interchangeable with WSL 2 / Ubuntu 24.04 scientific results. The WSL launchers do not automatically create, update, delete, or overwrite an existing environment.
