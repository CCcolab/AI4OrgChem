# Typical Reproduction and Evidence-Verification Programs

[中文](TYPICAL_PROGRAMS_zh-CN.md)

This page gives chemistry, quantum-chemistry, and computational-chemistry readers controlled entry points into the AI4OrgChem workflow: **scientific question → frozen protocol → electronic-structure calculation → numerical gates → machine result → scoped conclusion**.

> “Verification” here is not certification of the monograph. `PASS` means only that a specified computation or consistency check satisfied its registered inputs, methods, and tolerances.

## Choose a level

| Level | Entry point | QM executed | Typical resources | Status |
|---|---|---:|---|---|
| L0 | Frozen P01–P14 evidence verification | No | Standard Python; seconds | **Runnable** |
| L1 | P09 conditional-SCF core tests | Small tests | CPU; usually minutes | **Runnable** |
| L2 | P14 fixed-geometry technical smoke | Yes, STO-3G | WSL2; 8 threads | **Runnable** |
| L3 | P14 fixed-geometry scientific-level reproduction | Yes, B3LYPG/6-31G(d) | WSL2; 8 threads; adequate memory | **Runnable** |
| L4 | P14 five-parameter production optimization | Yes; expensive | WSL2; 8 threads; at least 13 GiB available memory | **Runnable; advanced** |

P09 cyclobutadiene smoke, the P10 benzene BLA scan, and the complete P09 aromatic-energy reproduction are the next public packaging targets. They are not shown with pretend commands before isolated output handling, dependency completion, and clean-clone execution pass.

## Common setup

The canonical scientific platform is **WSL 2 / Ubuntu 24.04**. From the repository root:

```bash
micromamba create -f reproducibility/environment.yml  # only if absent
source reproducibility/wsl/activate-ai4orgchem-public.sh
cd software
python -m pip install -e ".[science,test]"
cd ..
```

See the [English runbook](RUNBOOK_EN.md) and [platform matrix](PLATFORM_MATRIX_EN.md). Reproduction outputs belong under the Git-ignored `runs/reproduction/`; they must never overwrite frozen files under `evidence/`.

## L0 — frozen P01–P14 evidence verification

Purpose: verify that all fourteen published machine records can be read and that proposition IDs, verdicts, citations, key boundary states, and aggregate counts are internally consistent. No QM is rerun.

Process: enumerate P01–P14 → validate JSON/JSONL structure → compare frozen verdicts with the master statistics → check key P11/P12/P14 states → emit counts and status.

```bash
python software/scripts/validate_public_evidence.py
python software/scripts/validate_evidence_navigation.py
```

Expected output includes `status: PASS`, `propositions_checked: 14`, and `propositions_navigated: 14`. This verifies the published evidence package, not the physical correctness of the underlying calculations or peer-review status.

## L1 — P09 conditional-SCF core tests

Purpose: test the source-aligned infrastructure used by P09/P14: AO sigma/pi identity, fragment boundaries, Fock/overlap masking, exchange-integral classes, conditional SCF, and independent energy assembly.

Process: construct test matrices or PySCF AO objects → classify sigma/pi AOs → attach pi-fragment labels → zero registered cross-fragment Fock/overlap blocks → apply the frozen 15 exchange-integral classes → iterate conditional SCF → assemble one-electron, Coulomb, exchange, and nuclear terms → test electron count, energy closure, generalized commutator, and density idempotency.

```bash
cd software
python -m pytest -p no:cacheprovider \
  tests/test_p09_conditional_scf.py \
  tests/test_p09_energy_assembly.py \
  tests/test_p09_eri_mask.py
cd ..
```

All tests must pass. These are mathematical-contract tests, not a complete molecular reproduction of benzene ESE or cyclobutadiene ADE.

## L2 — P14 fixed-geometry technical smoke

Purpose: use the small STO-3G basis to establish that C12H6 geometry reconstruction, AO classification, conditional SCF, and the energy ledger execute on the user's machine.

Process: reconstruct planar D3h G/PLG source-proxy geometries from five published descriptors → ordinary closed-shell RKS at G → ordinary RKS anchor at PLG → sigma/pi classification and fragment mapping → conditional PLG SCF → technical endpoint → gates for 78 electrons, SCF convergence, reconstructed geometry, energy closure, commutator, and idempotency.

```bash
python software/scripts/run_p14_benzotricyclobutadiene_smoke.py
```

Outputs are written under `runs/reproduction/p14/`. `smoke_gate_verdict` should be `PASS`, but the STO-3G value is implementation evidence only and is ineligible for the P14 scientific verdict.

## L3 — P14 fixed-geometry scientific-level reproduction

Purpose: recompute the P14 fixed-geometry endpoint at B3LYPG/6-31G(d) on the public G/PLG source-proxy geometries and compare it with the frozen `67.086899 kcal/mol` value.

Process: hash public inputs → verify five-parameter reconstruction, atom order, planarity, and 78 electrons → ordinary G state → ordinary PLG density anchor → source-aligned conditional PLG state → direct-versus-memory-controlled energy equivalence → endpoint assembly → method, basis, SCF, electron-count, closure, commutator, idempotency, and memory gates.

```bash
python software/scripts/run_p14_benzotricyclobutadiene_source_level_fixed_geometry.py
```

See the [P14 input identity statement](../evidence/P01-P14/P14/inputs/README.md). These are reconstructed source-proxy coordinates because the historical Cartesian coordinates were not published.

## L4 — P14 five-parameter production optimization

Purpose: optimize the five planar D3h parameters independently for ordinary G and conditional PLG, then test both the structural response `dDelta-r(GP)` and the optimized endpoint.

Process: require at least 13 GiB available memory → generate frozen starts → optimize ordinary G at B3LYPG/6-31G(d) → qualify termination, gradient, and active bounds → optimize conditional PLG → repeat SCF, 78-electron, gradient, boundary, and conditional-state checks → calculate structure response and endpoint → issue `production_gate_verdict: PASS` only when every eligibility gate passes.

```bash
python software/scripts/run_p14_benzotricyclobutadiene_production_optimization.py
```

Frozen references are `dDelta-r(GP) = 0.172204 Å` and `67.679719 kcal/mol`. Numeric proximity alone is insufficient: method, basis, convergence, gradient, bounds, electron count, and energy closure must all qualify. The calculation covers only the registered planar D3h five-parameter subspace.

## Activation gates for the next entries

- **P09 cyclobutadiene smoke:** fixed planar rectangle → ordinary G-like RKS → sigma/pi classification → two-fragment DSI SCF → 15 exchange classes → independent ledger → numerical gates. It is not the final VDE/ADE.
- **P10 benzene BLA scan:** same-protocol P09 G/GL endpoints → `delta Ee`/`delta EN` decomposition → fixed mean C–C and C–H distances → ordinary RKS at `delta=0, 0.01, 0.02, 0.04, 0.06 Å` → independent nuclear Coulomb sum → curvature and plus/minus symmetry checks. It supports only the tested pathway.
- **Complete P09 reproduction:** cyclobutadiene G/DSI and conditional GL paths → VDE/ADE; benzene G/three-fragment DSI → restricted GL/GE1 optimizations → `ESE=delta EA-3 delta EA1` → blind comparison with frozen anchors.

Before activation, each entry must be included with its complete script and configuration, write only to `runs/reproduction/`, include geomeTRIC where required, contain no private paths or credentials, document resources, pass unit tests, pass a WSL2 clean-clone run, and reproduce the frozen evidence within registered tolerances.

## Reporting an independent reproduction

Include the repository tag or commit, OS, Python/PySCF versions, thread count, memory, exact command, SHA-256 of output JSON, `PASS/FAIL` status, and residual from the frozen result. Failed reproductions are scientifically useful and should not be discarded or replaced by success-only screenshots.
