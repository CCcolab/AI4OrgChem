> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# Target C tested-domain scientific labels v0.1

## Identity

- Data: `data/processed/target_c_tested_domain_scientific_labels_v0.1.jsonl`
- Generator: `scripts/generate_target_c_tested_domain_scientific_conclusion.py`
- Decision: ADR-0038
- Release protocol: `lfmo-sigma-pi/0.5-target-c-scoped-release`
- Status: final scoped scientific conclusion
- Records: 33 component records from 11 valid source-proxy points

## Scientific meaning

Each point contains three values in hartree:

1. `pi_pi_direct`: direct pi-pi contribution under the frozen source-native
   construction;
2. `orbital_response_total`: total orbital-response contribution;
3. `source_endpoint_E_FUD_minus_E_DSI3`: their closed endpoint.

The source convention assigns a destabilizing endpoint when
`E_FUD-E_DSI3 > 0`. All 11 valid endpoints are positive, so every record carries
the final scoped label
`pi_conjugation_endpoint_destabilizing_in_tested_source_proxy_domain`.

The component identity is

`pi_pi_direct + orbital_response_total = source_endpoint_E_FUD_minus_E_DSI3`.

## Coverage

- `diphenyl_imine`: 0, 5, 10, 15, 17, 20, 25, and 30 degrees
- `phenyl_vinyl_imine`: 0 and 17 degrees
- `divinyl_imine`: 0 degrees

Divinyl imine at 17 degrees is excluded because the LFMO construction did not
produce a square basis; no value was imputed.

## Intended and prohibited use

The data supports the final Target C tested-domain endpoint sign conclusion and
mechanistic analysis of direct-versus-response terms. It is not a production ML
dataset, is not training-eligible, and cannot support an all-molecule or
industrial-generalization claim.

## Provenance

Every JSONL record includes the geometry and LFMO basis hashes, DSI-3/FUD
configuration hashes, a combined fragment/state-contract hash, source artifact
path and SHA-256, source and generator Git commits, PySCF version, RHF method,
6-31G(d) basis, resource profile, and the public-source DOI/page range. The
validator is `scripts/validate_target_c_scoped_release.py`.
