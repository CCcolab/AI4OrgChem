# AI4S Agent capabilities and results

[Chinese original](CAPABILITIES_AND_RESULTS_zh-CN.md)

## Scientific task support

The Agent organizes fourteen falsifiable tasks with frozen data cards, protocols, reports, machine results, and validators. Version `v0.3.2` records all fourteen proposition-level determinations as consistent with the corresponding monograph propositions. P12 reached that determinate verdict through independent same-estimand N12/N14/N16 recalculations; the published v0.3.1 snapshot (13 consistent, one partially consistent) remains linked only as history. P05, P07, P11, P12, and P14 corrections and evidence-grade distinctions remain traceable.

## Molecular data and learning

The bounded engineering dataset contains 17 geometries, three molecular families, and five energy targets. Family-holdout checks found no conformer or family leakage. For the pi-pi target, three-fold family-holdout macro RMSE was 108.0 meV/atom for MACE and 108.2 meV/atom for NequIP. This demonstrates learnability only in the tested small-data domain.

## Active learning and symbolic exploration

The preregistered replay metric was 113.44 versus a random-selection median of 148.31, and two new QM labels were returned. After return, pi-sigma error improved by 0.58% while pi-pi error worsened by 2.75%: acquisition succeeded, but downstream model effects were mixed. A pi-pi PySR candidate beat an affine baseline in leave-one-family-out evaluation; the pi-sigma candidate failed the same blind test. These are exploratory relations, not universal physical laws.

## Evidence-grounded explanation

All nine internal delivery checks passed; this is not an external scientific benchmark. Answers retrieve frozen evidence with provenance, protocol, and scope. The Agent neither creates scientific labels nor changes P01–P14 conclusions.
