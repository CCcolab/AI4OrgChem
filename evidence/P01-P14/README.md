# P01-P14 Evidence Navigator

[中文导航](README_zh-CN.md)

This index connects every scoped scientific determination to its frozen data card, protocol, machine-readable result, and report. “Consistent” means consistent with the corresponding monograph proposition only inside the declared tested domain; it is not an identity reproduction, universal law, or institutional certification.

## Classification summary

- 12 consistent or scope-consistent;
- 2 partially consistent: P11 and P12;
- 0 globally inconsistent;
- 0 unknown.

| ID | Tested proposition | Determination | Key evidence and boundary | Files |
|---|---|---|---|---|
| P01 | Molecular-orbital representation must be distinguished from electron-density delocalization. | **Consistent** | Canonical/localized occupied-space transformations preserve the same-state density and RHF energy; this is an operational single-reference distinction. | [card](P01/data-card.md) · [protocol](P01/protocol.md) · [result](P01/result.json) · [report](P01/report.md) |
| P02 | Conjugation can accompany, rather than prevent, molecular distortion. | **Consistent** | Published structural values and homologous UV trends support the scoped direction; original CIF refinement was not repeated. | [card](P02/data-card.md) · [protocol](P02/protocol.md) · [result](P02/result.json) · [report](P02/report.md) |
| P03 | Electronic energy can favor twisting on the tested parent-NBA path while nuclear repulsion changes in the opposite direction. | **Consistent** | Relaxed fixed-torsion PES and electronic/nuclear decomposition for one source-aligned parent-NBA path; no cross-molecule universal claim. | [card](P03/data-card.md) · [protocol](P03/protocol.md) · [result](P03/result.json) · [report](P03/report.md) |
| P04 | LFMO-defined pi-pi endpoints can be destabilizing. | **Consistent** | All 11 technically valid tested source-proxy endpoints have the destabilizing sign; this does not imply every conjugated molecule has that sign. | [card](P04/data-card.md) · [protocol](P04/protocol.md) · [result](P04/result.jsonl) · [report](P04/report.md) |
| P05 | A pi-sigma source endpoint can be destabilizing. | **Scope-consistent** | The 17-degree Table 5-15 source-proxy endpoint is positive; the 0-degree point is indeterminate within tolerance. | [card](P05/data-card.md) · [protocol](P05/protocol.md) · [result](P05/result.jsonl) · [report](P05/report.md) |
| P06 | Nonbonded sigma-sigma interaction requires an explicit conditional-state definition and is not automatically identical to a classical steric energy. | **Consistent** | Both frozen Table 5-19 source-proxy endpoints are destabilizing under the declared PDSI/FUL state pair. | [card](P06/data-card.md) · [protocol](P06/protocol.md) · [result](P06/result.jsonl) · [report](P06/report.md) |
| P07 | A two-term “conjugative stabilization versus steric destabilization” account is insufficient for the tested mechanism. | **Scope-consistent** | The integrated argument requires pi-pi, pi-sigma, sigma-sigma, and response terms; energies from different state contracts are not summed. | [card](P07/data-card.md) · [protocol](P07/protocol.md) · [result](P07/result.json) · [report](P07/report.md) |
| P08 | A GL-defined butadiene conjugation energy can be positive, and hydrogenation references do not determine a unique sign. | **Consistent** | Frozen GL result is **+1.575676 kcal/mol**; the implementation is independent and not an identity reproduction of the historical program. | [card](P08/data-card.md) · [protocol](P08/protocol.md) · [result](P08/result.json) · [report](P08/report.md) |
| P09 | Aromatic and antiaromatic energies can be constructed from theoretical localized/virtual references. | **Consistent** | Cyclobutadiene ADE is **+53.822467 kcal/mol** and benzene ESE is **-37.412764 kcal/mol** in the frozen protocol. | [card](P09/data-card.md) · [protocol](P09/protocol.md) · [result](P09/result.json) · [report](P09/report.md) |
| P10 | Nuclear-repulsion variation is a major term along the tested benzene bond-alternation coordinate. | **Consistent** | Electronic and nuclear-repulsion contributions oppose one another; nuclear repulsion is not presented as an isolated cause independent of electronic structure. | [card](P10/data-card.md) · [protocol](P10/protocol.md) · [result](P10/result.json) · [report](P10/report.md) |
| P11 | Furan requires an LDE treatment, while substituted-benzene conjugative and inductive components must be separated. | **Partially consistent** | P11-A furan LDE is consistent. P11-B conjugative effect is **+1.180928** versus **+1.2 kcal/mol**, but both inductive diagnostics are negative (**-0.335714**, **-0.580151**) while the monograph value is **+0.49**. Historical cyanobenzene Cartesian coordinates were unavailable. | Furan: [card](P11/furan-data-card.md) · [protocol](P11/furan-protocol.md) · [result](P11/furan-result.json) · [report](P11/furan-report.md). Substituent: [card](P11/substituent-data-card.md) · [protocol](P11/substituent-protocol.md) · [result](P11/substituent-result.json) · [report](P11/substituent-report.md) |
| P12 | Large annulenes approach polyene-like energetic behavior, but the exact size boundary is estimator-dependent. | **Partially consistent** | The qualitative large-ring trend agrees. The monograph ledger places its onset at **N=16/18**, whereas an independent ASE trend places energetic nonaromaticity at **N>30**. Because the estimands differ, this is a retained onset disagreement rather than a same-estimator refutation. | [card](P12/data-card.md) · [protocol](P12/protocol.md) · [result](P12/result.json) · [report](P12/report.md) |
| P13 | Polycyclic benzenoid analysis requires the tested GL/position/energy rule hierarchy rather than a single local count. | **Consistent** | Independent graph enumeration and the published energy ledger support the scoped rule hierarchy; the complete historical optimization panel was not rerun. | [card](P13/data-card.md) · [protocol](P13/protocol.md) · [result](P13/result.json) · [report](P13/report.md) |
| P14 | Pi interaction can contribute to distortion in a strained aromatic system. | **Consistent** | The frozen C12H6 source-proxy endpoint is **+67.086899 kcal/mol**; the result is not generalized to the complete strained-aromatic panel. | [card](P14/data-card.md) · [protocol](P14/protocol.md) · [result](P14/result.json) · [report](P14/report.md) |

## How to verify

From the repository root:

```bash
python software/scripts/validate_public_evidence.py
```

The validator checks all fourteen packaged result records and must return `status: PASS`. The complete cross-proposition matrix is available in [`manuscripts/P01-P14_evidence_matrix_zh-CN.md`](../../manuscripts/P01-P14_evidence_matrix_zh-CN.md).

## Evidence boundaries

- Processed evidence and frozen conclusions are included; raw copyrighted source material and private run directories are not.
- `production_label=false` in a frozen result records the scientific/ML boundary of that artifact and must not be silently changed.
- Source-proxy, source-aligned reconstruction, and historical identity reproduction are distinct evidence levels.
- AI predictions and symbolic candidates do not modify P01-P14 determinations.
