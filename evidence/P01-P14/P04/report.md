> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# Target C tested-domain scientific conclusion

- Valid tested points: `11`
- Endpoint verdict: **source_proxy_endpoint_destabilization_supported_across_all_valid_tested_points**
- Final scoped label: **pi_conjugation_endpoint_destabilizing_in_tested_source_proxy_domain**
- Direct-term verdict: `rejected_by_negative_direct_counterexample`
- Orbital-response verdict: `geometry_and_family_dependent`

| Family | Angle | pi-pi direct (Eh) | Orbital response (Eh) | E_FUD-E_DSI3 (Eh) |
|---|---:|---:|---:|---:|
| diphenyl_imine | 0.0 | +0.025077133649 | +0.044482034476 | +0.069559168126 |
| diphenyl_imine | 5.0 | +0.036666346278 | +0.032586974432 | +0.069253320713 |
| diphenyl_imine | 10.0 | +0.069780656497 | -0.001434609740 | +0.068346046759 |
| diphenyl_imine | 15.0 | +0.119678232901 | -0.052812650159 | +0.066865582736 |
| diphenyl_imine | 17.0 | +0.142786269325 | -0.076664687111 | +0.066121582213 |
| diphenyl_imine | 20.0 | +0.179161316184 | -0.114309729441 | +0.064851586756 |
| diphenyl_imine | 25.0 | +0.239539422466 | -0.177191671802 | +0.062347750638 |
| diphenyl_imine | 30.0 | +0.291757777393 | -0.232360471745 | +0.059397305663 |
| divinyl_imine | 0.0 | -0.044225762300 | +0.109169110157 | +0.064943347857 |
| phenyl_vinyl_imine | 0.0 | +0.148501083702 | -0.076301068687 | +0.072200015016 |
| phenyl_vinyl_imine | 17.0 | +0.251717417716 | -0.182973856051 | +0.068743561657 |

## Scientific conclusion

Under the source-directed convention `E_FUD-E_DSI3 > 0`, every technically valid point in the tested source-proxy domain has a destabilizing total endpoint. This supports a tested-domain endpoint destabilization law.

The stronger statement that the pi-pi direct term is always destabilizing is rejected: divinyl imine at 0 degrees has a negative direct term and a larger positive response, while its endpoint remains positive. Orbital response is likewise geometry- and family-dependent.

## Boundary

- Excluded point: `divinyl_imine:17.0` because `non_square_lfmo_basis_no_scientific_value_emitted`.
- The law is final for the tested valid source-proxy domain, not a theorem for all molecules or all geometries.
- Production and AI-training eligibility remain false.
- Every released record carries geometry, LFMO/state-contract, source-artifact, engine, method, basis, resource-profile, and Git provenance.
