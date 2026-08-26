> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# Independent LFMO protocol v0.5 - Target C scoped scientific release

- Protocol ID: `lfmo-sigma-pi/0.5-target-c-scoped-release`
- Status: accepted scoped scientific release; non-production
- Date: 2026-08-16
- Inherits: `lfmo-sigma-pi/0.4-draft`
- Decision: ADR-0038
- Original program code used: no

## 1. Purpose

Version 0.5 does not replace or broaden the v0.4 LFMO construction contract.
It adds one narrowly defined scientific-release exception for Target C after
the accepted source-proxy decision, the source-native DSI-3/FUD reconstruction,
and the tested-domain sign analysis.

All v0.4 prohibitions remain in force for Target A, Target B, production ML
labels, industrial generalization, and any molecular or energetic quantity not
explicitly listed below.

## 2. Released observable

For a technically valid Target C point, define

`Delta E_endpoint(theta) = E_FUD(theta) - E_DSI3(theta)`.

The source-directed sign convention is:

- `Delta E_endpoint > +1.0e-8 Eh`: destabilizing endpoint;
- `Delta E_endpoint < -1.0e-8 Eh`: stabilizing endpoint;
- otherwise: indeterminate within tolerance.

The source-native DSI-3 and FUD states are solved independently with their own
source-local LFMO constructions. A DSI-3 basis may be used only after both AO
densities are frozen, to report the exact direct-plus-response identity. FUD
must not be re-solved on the DSI-3 reporting basis.

## 3. Accepted tested domain

The released domain contains 11 valid source-proxy points:

- diphenyl imine at 0, 5, 10, 15, 17, 20, 25, and 30 degrees;
- phenyl-vinyl imine at 0 and 17 degrees;
- divinyl imine at 0 degrees.

Divinyl imine at 17 degrees is excluded because the LFMO construction did not
form a square basis. No value is imputed and no threshold is loosened.

## 4. Released conclusion

All 11 endpoint values are positive, from `+0.059397305663` to
`+0.072200015016 Eh`. The final scoped label is

`pi_conjugation_endpoint_destabilizing_in_tested_source_proxy_domain`.

The direct pi-pi term is not assigned a universal sign. Divinyl imine at 0
degrees is a retained negative direct-term counterexample. Orbital response is
also geometry- and family-dependent.

## 5. Required provenance and closure

Every released record must contain:

- family, angle, geometry hash, and LFMO basis hash;
- DSI-3, FUD, and combined fragment/state-contract hashes;
- source artifact path and SHA-256;
- source calculation and release-generator Git commits;
- engine/version, method, basis, and resource profile;
- source DOI/pages, sign convention, value, and unit.

Each point must contain exactly the direct pi-pi, total orbital-response, and
endpoint records and satisfy

`pi_pi_direct + orbital_response_total = E_FUD - E_DSI3`

within `1.0e-9 Eh`.

## 6. Release boundary

This protocol authorizes a final scientific interpretation only for the tested
valid source-proxy domain. It does not authorize:

- historical Cartesian-coordinate identity;
- a theorem for all molecules or geometries;
- universal positivity of the isolated direct pi-pi term;
- final pi-sigma, sigma-sigma, steric, or aromatic-energy conclusions;
- production ML labels, MACE/PySR training, or industrial generalization.

The overall 24-week AI4OrgChem program and its production data/AI gates remain
incomplete.
