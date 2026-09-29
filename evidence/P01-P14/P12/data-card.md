# P12 annulene evidence data card v0.2

## Determination

**P12 is consistent with the monograph.** The machine verdict is
`P12_CONSISTENT`, validated as `PASS_P12_CONSISTENT`.

The verdict is based on three independently recalculated, same-estimand
configurations: N12 / `[12]-555`, N14 / `[14]-665`, and N16 / `[16]-5555`.
N18, N20, and N22 were not used for this determination and are not pending
requirements for v0.3.2.

## Method

- geometry and energy: fully planar `B3LYPG/6-311G(2df,p)`;
- original monograph program code: not used;
- estimand: `ESE = delta_EA - sum(delta_EAm)` and
  `CESE = ESE - sum(delta_EnAm)`;
- N16: all 28 GE pairs calculated directly, with no symmetry weighting;
- historical-program identity and digit-for-digit numerical reproduction: not
  claimed.

## Results

| Point | delta EA | ESE | CESE | Source CESE | Registered check |
|---|---:|---:|---:|---:|---|
| N12 | +13.237142 | +1.853187 | +2.887010 | +2.59 | positive CESE: pass |
| N14 | -6.366236 | -16.928395 | -15.947079 | -16.28 | negative delta EA/ESE/CESE: pass |
| N16 | +15.804323 | -1.622341 | -0.339527 | -0.65 | relative CESE 2.103137% <= 10%: pass |

Units are kcal/mol except relative CESE. All registered direction checks pass,
and no same-estimand opposing result was established.

## Machine records

- [v0.3.2 determination](result.json)
- [N12 ledger](n12-same-basis-ledger.json)
- [N14 ledger](n14-same-basis-ledger.json)
- [N16 ledger](n16-same-basis-ledger.json)
- [historical v0.3.1 result](result-v0.3.1-historical.json)

The v0.3.1 result is preserved for version history and is not the current P12
determination.
