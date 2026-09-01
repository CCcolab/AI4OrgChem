#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: run_wp1_qp2_cipsi.sh INPUT_DIR RUN_ROOT" >&2
  exit 2
fi

INPUT_DIR="$1"
RUN_ROOT="$2"
QP_ROOT="${PROJECT_ROOT}/opt/ai4orgchem-v02-cipsi/qp2-v2.2.2"
ENV_PREFIX="${PROJECT_ROOT}/micromamba/envs/ai4orgchem-v02-cipsi"

case "${RUN_ROOT}" in
  ${PROJECT_ROOT}/ai4orgchem-v02-runs/wp1/qp2-cipsi*) ;;
  *) echo "Refusing unsafe WP1 QP run directory: ${RUN_ROOT}" >&2; exit 2 ;;
esac

test -f "${INPUT_DIR}/wp1_qp_input_manifest.json"
test -f "${INPUT_DIR}/cbd_d2h.xyz"
test -f "${INPUT_DIR}/cbd_d4h.xyz"

export CPATH="${ENV_PREFIX}/include"
export C_INCLUDE_PATH="${ENV_PREFIX}/include"
export LIBRARY_PATH="${ENV_PREFIX}/lib"
export LD_LIBRARY_PATH="${ENV_PREFIX}/lib"
export PKG_CONFIG_PATH="${ENV_PREFIX}/lib/pkgconfig:${ENV_PREFIX}/share/pkgconfig"
export OMP_NUM_THREADS=8
export QP_ROOT
export PYTHONPATH="${PYTHONPATH:-}"
# QP 2.2.2's etc/ocaml.rc tests $OPAMROOT before assigning it.  Define the
# variable explicitly so the frozen runner can retain `set -u`.
export OPAMROOT="${OPAMROOT:-}"
# The legacy qp.rc wrapper also assumes this variable exists before the first
# EZFIO database is selected.
export EZFIO_FILE="${EZFIO_FILE:-}"
source "${QP_ROOT}/quantum_package.rc"

mkdir -p "${RUN_ROOT}"
cp "${INPUT_DIR}/wp1_qp_input_manifest.json" "${RUN_ROOT}/"

for endpoint in d2h d4h; do
  endpoint_root="${RUN_ROOT}/${endpoint}"
  mkdir -p "${endpoint_root}"
  cp "${INPUT_DIR}/cbd_${endpoint}.xyz" "${endpoint_root}/"
  cd "${endpoint_root}"
  ezfio="cbd_${endpoint}.ezfio"

  qp create_ezfio -b cc-pvdz -c 0 -m 1 -o "${ezfio}" "cbd_${endpoint}.xyz" \
    2>&1 | tee create_ezfio.log
  qp set_file "${ezfio}"
  qp set scf_utils n_it_scf_max 150
  qp run scf 2>&1 | tee scf.log
  # QP 2.2.2's --small branch has an upstream indentation defect.  For the
  # present H/C-only system its default rule is exactly equivalent: one C 1s
  # orbital per carbon and none for hydrogen.  Call the tool directly so its
  # arguments are not hidden by the generic `qp` wrapper.
  qp_set_frozen_core "${ezfio}" 2>&1 | tee frozen_core.log
  qp set_file "${ezfio}"
  qp set determinants n_states 1
  qp set determinants expected_s2 0.0
  qp set determinants s2_eig True
  qp set determinants read_wf False
  qp set perturbation do_pt2 True
  qp set perturbation pt2_max 0.0002
  qp set determinants n_det_max 50000
  qp set davidson_keywords threshold_davidson 1.e-10
  qp set davidson_keywords n_states_diag 4
  qp run fci 2>&1 | tee cipsi.log

  ezfio get hartree_fock energy > hf_energy.txt
  ezfio get fci energy > variational_energy.txt
  ezfio get fci energy_pt2 > variational_plus_pt2_energy.txt
  ezfio get determinants n_det > n_det.txt
done

printf '%s\n' 'WP1_QP2_CIPSI_ENDPOINTS_COMPLETE'
