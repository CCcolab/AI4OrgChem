# Runtime Platform Matrix

## Canonical environment

AI4OrgChem scientific calculations and AI training results were produced and validated under **WSL 2 / Ubuntu 24.04**. WSL 2 is not a conceptual requirement of the method, but it is the canonical platform supported by the present evidence. Untested platforms must not be described as equivalent reproductions.

| Component | Canonical/recommended platform | Native Windows status | First GitHub release commitment |
|---|---|---|---|
| Markdown and JSON/JSONL evidence | Any platform | Supported | Fully supported |
| `validate_public_evidence.py` | Python 3.12; WSL/Linux preferred | Expected to run | Frozen-result integrity check |
| NumPy LFMO subspace and mask tests | WSL 2 / Linux | May run; not canonical | Code and tests included |
| PySCF conditional-SCF and quantum-chemistry workflow | WSL 2 / Ubuntu 24.04 | Not certified as equivalent | Core implementation included; full expensive reruns not promised |
| MACE GPU training | WSL 2 with CUDA-12.6-compatible PyTorch | Not certified | Frozen evaluation summary only |
| NequIP GPU comparison | WSL 2, isolated environment, CUDA | Not certified | Frozen evaluation summary only |
| PySR symbolic search | WSL 2 with Julia/Python runtime | Not certified | Frozen blind-test conclusion only |
| Read-only WebUI/evidence agent | Local browser and controlled backend | Local delivery, not a release prerequisite | Architecture, capability, result, and limitation documents only |

## Environment isolation

- Existing user WSL 2 environments must not be overwritten or upgraded;
- the public CPU review environment is named `ai4orgchem-public` and is distinct from historical project runtimes;
- historical MACE and NequIP validation used separate environments because their `e3nn` requirements differed;
- the first GitHub `environment.yml` does not claim to recreate both GPU environments. GPU lockfiles belong in a later model/data archive release.
