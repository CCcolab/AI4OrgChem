#!/usr/bin/env bash
set -euo pipefail

project_mamba_exe="${MAMBA_EXE:-${HOME}/.local/bin/micromamba}"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-${HOME}/micromamba}"
export PYTHONNOUSERSITE=1

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
clone_root="$(cd -- "${script_dir}/../.." && pwd -P)"
if [[ -n "${AI4ORGCHEM_PUBLICATION_ROOT:-}" ]]; then
    publication_root="${AI4ORGCHEM_PUBLICATION_ROOT}"
elif [[ -f "${clone_root}/software/scripts/validate_public_evidence.py" ]]; then
    publication_root="${clone_root}"
else
    publication_root="/opt/ai4orgchem/publication"
fi

if [[ ! -x "${project_mamba_exe}" ]]; then
    echo "micromamba not found: ${project_mamba_exe}" >&2
    return 1 2>/dev/null || exit 1
fi

eval "$("${project_mamba_exe}" shell hook --shell bash)"
if ! micromamba env list | awk '{print $1}' | grep -qx 'ai4orgchem-public'; then
    echo "Environment ai4orgchem-public does not exist." >&2
    echo "Inspect existing environments first, then create it explicitly from ${publication_root}/reproducibility/environment.yml if needed." >&2
    return 1 2>/dev/null || exit 1
fi

micromamba activate ai4orgchem-public
export AI4ORGCHEM_PUBLICATION_ROOT="${publication_root}"
cd "${AI4ORGCHEM_PUBLICATION_ROOT}"

echo "AI4OrgChem public WSL environment active"
echo "Environment: ${CONDA_DEFAULT_ENV:-ai4orgchem-public}"
echo "Publication root: ${AI4ORGCHEM_PUBLICATION_ROOT}"
echo "Existing WSL environments were not changed"
