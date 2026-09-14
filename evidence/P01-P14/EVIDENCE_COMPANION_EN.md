# P01–P14 English evidence companion

This page provides an English route from the [evidence navigator](README.md) to the data scope, protocol, and report for each proposition. It is a **review companion, not a replacement for the frozen original records**. The linked machine-readable results retain their original values and status. The original data cards, protocols, and reports remain available in the [Chinese navigator](README_zh-CN.md) (intentional language switch). The [English evidence matrix](../../manuscripts/P01-P14_evidence_matrix_EN.md) gives the proposition-level comparison in one table.

“Consistent” below means consistent with the monograph proposition in the registered tested domain, not universal validity or historical program identity. In particular, the published `v0.3.1` P12 label is historical; consult the [bilingual P12 corrigendum](../../P12_CORRIGENDUM.md#english) for its current interpretation.

## P01 — orbital representation versus electronic delocalization

### P01 data card

The same-state control is ethene at RHF/6-31G(d), comparing canonical, Boys, and Pipek–Mezey occupied orbitals. A separate named-state LFMO DSI-3/FUD comparison is used for a conditional energy difference. NBO and BLW were mapped conceptually but not run numerically. [Machine result](P01/result.json).

### P01 protocol

An occupied-space unitary rotation changes orbital appearance without changing the underlying Slater determinant's density or RHF energy. A comparison of independently defined restricted electronic states is a different operation and may have an energy difference. The protocol therefore separates orbital representation, electron density, and state-defined energy delocalization.

### P01 report

The ethene controls agree in density (maximum relative residual `7.207e-16`) and RHF energy (maximum residual `5.684e-14 Eh`), while the LFMO state comparisons are not occupied-orbital gauge rotations. This supports the conceptual distinction within the single-reference tested scope. It does not supply a unique delocalization index for every electronic system or claim NBO/BLW numerical equivalence.

## P02 — conjugation and molecular distortion

### P02 data card

The evidence is a published-value reanalysis of ten UV targets in Table 1-1 and one preregistered crystal-structure pair with two directional observables. Raw CIF refinement and new crystal measurements were not performed. [Machine result](P02/result.json).

### P02 protocol

The test compares published UV reference-series trends and the structural pair `1-1-(1,1)` versus `1-1-(1,2)`. The prespecified question is whether stronger participation of the aromatic branch necessarily coincides with more planarity and a shorter C–N bond. It is an association test, not a controlled causal intervention.

### P02 report

In the selected pair, the reported torsions are `33.6°` and `31.4°`, and the C–N distances are `1.430` and `1.423 Å`; both differences oppose an unconditional planarization/shortening prediction. The published-value scope supports the proposition's possibility claim, not a universal distortion law or independent validation of the source crystallography.

## P03 — parent NBA torsion energy ledger

### P03 data card

The sole molecule is neutral singlet parent N-benzylideneaniline (NBA). PySCF Gaussian-style B3LYP (`B3LYPG`)/6-311G(d,p) supplies total, electronic, and nuclear-repulsion energies at fixed torsions `0°, 20°, 40°, 60°`. [Machine result](P03/result.json).

### P03 protocol

At each nonzero torsion, the remaining Cartesian degrees of freedom are relaxed. The coordinate is the preregistered C(ortho)–C(ipso)–N–C(imine) torsion. The decision concerns the directions of `ΔEe`, `ΔEN`, and `ΔE` on this one relaxed path, not an LFMO attribution or an unrestricted search over all conformers.

### P03 report

Relative to `0°`, the sampled `40°` geometry has `ΔEe=-1.070056911 Eh`, `ΔEN=+1.068209105 Eh`, and `ΔE=-1.159516 kcal/mol`. It is the lowest **of four sampled points**, not a continuously located minimum. Opposing component changes support the registered path-level observation but alone do not prove a unique causal mechanism or a universal NBA rule.

## P04 — LFMO π–π endpoints

### P04 data card

The released Target C set contains `33` component records at `11` technically valid source-proxy points across diphenyl imine, phenyl-vinyl imine, and divinyl imine. One of twelve attempted points was excluded by the technical gate. [Machine endpoint records](P04/result.jsonl).

### P04 protocol

The declared observable is the conditional-state endpoint `E_FUD−E_DSI3`; values above `+1.0e-8 Eh` are called destabilizing under this sign convention. Direct π–π and orbital-response terms are recorded separately. The valid domain comprises eight diphenyl-imine angles, two phenyl-vinyl-imine angles, and one divinyl-imine angle.

### P04 report

All `11/11` valid endpoints have the destabilizing sign. The direct term itself has a negative counterexample, and orbital response varies by geometry and family; neither is licensed as a fixed-sign universal mechanism. The conclusion is endpoint sign regularity **in this tested source-proxy domain**, not a production ML label.

## P05 — π–σ seven-angle continuation

### P05 data card

One fixed-parent diphenyl-imine source-proxy is evaluated at `0°, 5°, 10°, 17°, 25°, 35°, 45°`. The `0°/17°` records were frozen anchors; five additional angles are new quantum-chemical calculations. [Seven-angle result](P05/seven-angle-result.json) · [historical anchors](P05/result.jsonl).

### P05 protocol

The same PySCF RHF/6-31G(d) method and source-defined G/FUD conditional-state contract are used at all seven geometries. The observable is `E_G−E_FUD`, decomposed into direct interaction and orbital response. The decision sign threshold is `±1.0e-8 Eh`; `0°` is the zero control.

### P05 report

All six nonzero endpoints are positive: from `+0.491410 kcal/mol` at `5°` to `+36.955403 kcal/mol` at `45°`; `17°` is `+5.729850 kcal/mol`. This strengthens the within-system sign result without changing molecule, basis, or estimator. It does not establish the same sign for other molecules or arbitrary conformations.

## P06 — nonbonded σ–σ conditional endpoint

### P06 data card

The source-proxy parent NBA geometry is tested at `0°` and `17°`, with RHF/STO-3G single points and FUL/PDSI conditional states. There are two geometries, not a continuous angle scan or multiple molecules. [Machine endpoint records](P06/result.jsonl).

### P06 protocol

The observable is `E_PDSI−E_FUL`; positive values above `+1.0e-8 Eh` indicate a destabilizing net source-defined nonbonded σ–σ endpoint. The underlying geometries came from constrained B3LYPG/6-311G(d,p) candidates. This source-defined comparison must not be treated as a generic variational RHF interaction energy.

### P06 report

The two endpoints are `+0.067957103709 Eh` (`+42.643726 kcal/mol`) and `+0.062753624288 Eh` (`+39.378494 kcal/mol`). Both have the registered destabilizing sign. They cannot be directly added to differently defined P04/P05 energies or generalized to every molecule's classical steric repulsion.

## P07 — multicomponent path accounting

### P07 data card

P07 combines the separately scoped P04–P06 propositions with an independent **same-Hamiltonian audit of already computed five-state results** at `0°` and `17°`. The audit was a reanalysis, not a newly executed QM task. [Synthesis](P07/result.json) · [same-Hamiltonian audit](P07/same-hamiltonian-audit-result.json).

### P07 protocol

Cross-protocol Hartree values from P04, P05, and P06 are not summed. Within the same RHF/STO-3G geometry/state contract, compare the naive terms `(G−FUD)+(FUD−DSI2)+(PDSI−FUL)` with the missing bridge `DSI2−PDSI`, or use the complete path `(G−FUD)+(FUD−DSI2)+(DSI2−FUL)=G−FUL`.

### P07 report

The naive residuals are `+0.335760104092 Eh` at `0°` and `+0.333815958695 Eh` at `17°`; the corresponding bridge terms exactly cancel them, leaving zero path-complete residual. This supports the insufficiency of the naive two-/three-term account in the tested contract. Evidence identity is `INDEPENDENT_COMPUTATIONAL_AUDIT_PLUS_DERIVED_SYNTHESIS`, not a universal torsional mechanism or cross-protocol energy decomposition.

## P08 — GL-defined butadiene energy

### P08 data card

The molecule is gas-phase, closed-shell singlet trans-1,3-butadiene at B3LYPG/6-31G(d). The GL(2014) state uses source-defined blocking of inter-fragment π Fock/overlap coupling and selected exact-exchange contributions, with constrained planar optimization. This is an independent-code **source-aligned** reconstruction, not historical PC-GAMESS program identity. [Machine result](P08/result.json).

### P08 protocol

The primary quantity is `ΔEA=E(G)−E(GL,2014)`; its positive sign means destabilization **relative to that GL reference**, not a universal statement about conjugation. The 2011 and 2014 GL definitions are not mixed. Separate subtests inspect hydrogenation-reference dependence and the central C–C bond length.

### P08 report

`ΔEA=+1.575676 kcal/mol` versus approximately `+1.5` in the monograph. The central bond is `1.457809 Å` in G and `1.454394 Å` in GL. Different hydrogenation references do not fix a unique sign. The result supports the three registered butadiene subclaims under this source-aligned protocol; it is not a method-independent physical-law test or a production label.

## P09 — benzene and cyclobutadiene reference energies

### P09 data card

The two systems are gas-phase closed-shell singlet benzene and cyclobutadiene at B3LYPG/6-31G(d). The independent implementation includes AO σ/π classification, conditional SCF, Fock/overlap blocking, and selected exchange-integral deletions. Its status is source-aligned, not original-program identity. [Machine result](P09/result.json).

### P09 protocol

Cyclobutadiene is compared through G/DSI/GL, with `VDE=E(G)−E(DSI@G)` and `ADE=E(G)−E(GL)`. Benzene uses G/GL/GE-1 and three equivalent pair increments, giving `ESE=ΔEA−3ΔEA1`. The preregistered quantitative-support tolerance for the principal source comparisons was `5 kcal/mol`.

### P09 report

Cyclobutadiene gives `VDE=+44.182857` and `ADE=+53.822467 kcal/mol`, versus `+44.2` and `+53.6` in the source. Benzene gives `ESE=-37.412764` versus `-36.3 kcal/mol`: an absolute difference of `1.112764` (`≈3.07%`). The benzene difference closes algebraically through the two intermediate quantities; its unique historical cause is not established. The signs and approximate magnitudes support the registered source-defined propositions, not exact numerical identity or a unique aromatic-energy definition.

## P10 — benzene energy-component ledger

### P10 data card

One benzene system at B3LYPG/6-31G(d) is tested through the P09 G/GL endpoint decomposition and a five-point ordinary RKS bond-alternation path holding mean C–C and C–H distances fixed. [Machine result](P10/result.json).

### P10 protocol

For the endpoint, compare `ΔEe=Ee(G)−Ee(GL)`, `ΔEN=EN(G)−EN(GL)`, and their total. On the D3h alternating-bond path, use `ra=r0−δ`, `rb=r0+δ` and check whether electronic and nuclear-repulsion changes oppose each other and which absolute change is larger. This is a coordinate-specific energy ledger, not an intervention that isolates nuclear repulsion as a free-standing cause.

### P10 report

The G/GL endpoint has `ΔEe=+144.790178`, `ΔEN=-164.653082`, and `ΔE=-19.862904 kcal/mol`. Across the nonzero bond-alternation points, the electronic change is negative and nuclear-repulsion change positive with larger absolute magnitude; the total increases. The five RKS points and 17 acceptance checks passed. The registered path-level proposition is supported; no universal causal claim for all aromatic systems follows.

## P11-A — furan local delocalization energy

### P11-A data card

The sole system is planar `C2v` furan, gas-phase closed-shell singlet, at B3LYPG/6-31G(d). Its π fragments are the oxygen p lone-pair group and the two C=C groups. G, GL, and GE states are independently optimized in the same restricted planar space. [Machine result](P11/furan-result.json).

### P11-A protocol

The source-2007 restricted-geometry construction blocks specified inter-fragment π AO Fock/overlap couplings **without** the two-electron exchange deletion used in other method versions. `ΔEA=E(G)−E(GL)` and local `ΔEAm=E(GEm)−E(GL)` are compared; the two equivalent O–C=C increments are related by symmetry.

### P11-A report

The computed total increment is `ΔEA=+33.509904 kcal/mol`; the single-pair terms are `+28.500658` and `+22.930178 kcal/mol`, giving `ΣΔEAm=+74.361013 kcal/mol`. This supports the source-aligned furan LDE assessment in one molecule. Other vertical or half-adiabatic LDE definitions are complementary but not identical estimands.

## P11-B — cyanobenzene substituent effect

### P11-B data card

One cyanobenzene and one benzene comparator are represented by ten and three source-defined states, respectively. Every state is independently optimized with **all atoms constrained to `z=0`**, at source-2007 B3LYP/6-31G(d). [Machine result](P11/substituent-result.json) · [state records](P11/optimized-states/) · [superseded fixed-geometry audit](P11/substituent-fixed-geometry-audit-result.json).

### P11-B protocol

At each SCF iteration, specified inter-fragment π AO Fock/overlap blocks are suppressed; the two-electron integrals remain, and the physical one-electron operator is not additionally zeroed. The state-specific protocol uses G, GL-I, GE1–GE3, GL-II, GE4–GE7 for cyanobenzene and G/GL/GE1 for benzene. CE and IE are **differences of ESEs under the same method**, not quantities taken from unlike fixed-geometry and optimized-state contracts.

### P11-B report

The computed `ESE(SB)=-37.352830`, `ESE(Ph)=-38.525952`, and `ESE(benzene)=-39.016031 kcal/mol` give `CE=+1.173122` and `IE=+0.490079 kcal/mol`, near source values `+1.2` and `+0.49`. All `13/13` states converged. The older fixed-geometry IE sign is retained only as a superseded audit diagnostic. This is a one-system source-aligned result, not recovery of unpublished historical Cartesian coordinates or program identity.

## P12 — annulene size boundary

### P12 data card

The published six-point source ledger covers `N=12, 14, 16, 18, 20, 22`, with VDE, ESE, CESE, `ΔEA`, local increments, and a `4n/4n+2` split. The six printed values received **arithmetic/source-ledger checks**, not six independent quantum-chemical reruns. [Frozen machine result](P12/result.json).

### P12 protocol

The registered panels are `12/16/20` for `4n` and `14/18/22` for `4n+2`. Within the monograph ledger, CESE relative to local increments decreases and `ΔEA` changes sign in the `4n+2` series. A separate ASE study is a **different-estimand** complement: comparing its `N>30` boundary directly with the source CESE `N=16/18` onset is not a same-estimand agreement or counterexample.

### P12 report

The `v0.3.1` result retains a **historical “partially consistent” label**, but its former cross-estimand opposing-subclaim rationale has been withdrawn. The source-ledger large-ring direction is compatible; precise CESE onset under fully matched method, basis, state, and geometry remains independently unconfirmed. Local N12/N14/N16 candidate numbers were not added to the public package, and there is no independent N18/N20/N22 CESE panel. Do not interpret this label as “one verified true subclaim and one verified false subclaim”; see the [P12 corrigendum](../../P12_CORRIGENDUM.md#english).

## P13 — polycyclic benzenoid rule hierarchy

### P13 data card

The inputs are a published ESE/CESE energy ledger and independently enumerated Kekulé graph candidates for linear acenes. The output is a scoped rule-hierarchy check, not a new QM optimization of every candidate. [Machine result](P13/result.json).

### P13 protocol

Check the printed-precision identities `ESE=ΔEA−ΣΔEAm` and `CESE=ESE−ΣΔEnAm`, plus per-π-electron normalization. Candidate selection first requires the GL sextet condition `N_GL=N_db+1`; the energy rule is applied **only among eligible candidates**. A graph-enumeration lane independently checks candidate counts.

### P13 report

For 2–7 fused acene rings, enumeration yields Kekulé candidate counts `3–8` and GL-qualified counts `1–6`. The 14 published ledger rows close at printed precision. A held-out candidate illustrates that the globally highest-energy structure can violate the GL condition, while the source-selected candidate wins within the eligible set. The rule order is supported in the tested graph/ledger domain; the original restricted-geometry QM calculations were not rerun.

## P14 — strained aromatic π-distortivity

### P14 data card

The sole system is source structure 10-12, benzotricyclobutadiene `C12H6`, with a preregistered planar `D3h` five-parameter source-proxy geometry. The corrected evidence gate excludes an older STO-3G technical smoke test from scientific classification. [Machine result](P14/result.json) · [lower-level records](P14/processed/).

### P14 protocol

The test compares ordinary G and π-localized PLG states at B3LYPG/6-31G(d), with independently optimized five-parameter geometries and registered gradient, structure, energy, and eligibility checks. The target is whether the π operation contributes to the central-ring bond-length alternation beyond a purely angle-strain description. It is not a full Cartesian conformer/frequency survey.

### P14 report

Qualified production optimization gives `dΔr=+0.172204 Å` versus the source `+0.179 Å`, and an endpoint `+67.679719 kcal/mol` versus `+67.08`. The separate fixed-geometry source-level anchor is `+67.086899 kcal/mol`; it is not substituted for the production optimization. The repaired gate and production result support consistency in the one `C12H6` source-proxy system, not all strained aromatic molecules.
