> **公开版说明（2026-08-26）：** 本文是命题关闭时形成的冻结证据快照。其中“未启动/禁用”等阶段性措辞只描述当时的任务边界，不代表项目当前进度；当前总状态以 `project/P01-P14_MASTER_TABLE_zh-CN.md` 和 `ai4s-agent/EVALUATION_SUMMARY.json` 为准。

# P03 parent NBA relaxed PES protocol v0.1

## Scientific question

For parent N-benzylideneaniline (NBA, monograph molecule 2-1), does distortion from the planar constrained geometry toward the preferred twisted geometry show decreasing electronic energy, increasing nuclear repulsion, and decreasing total molecular energy at the same time?

This is the project-level falsifiable form of the monograph's Chapter 2 driving-force/resistance proposition. It tests the direction of total electronic and nuclear terms; it does not assign the trend to a specific LFMO interaction.

## Frozen system

- Molecule: parent NBA only, neutral singlet, gas phase.
- Initial geometry: existing project B3LYPG/6-311G(d,p) constrained-planar optimized geometry, SHA-256 recorded in its geometry artifact.
- Electronic structure: PySCF Gaussian-style B3LYP (`B3LYPG`) with 6-311G(d,p), grid level 3.
- Scan: relaxed fixed torsion at 0, 20, 40 and 60 degrees.
- Coordinate: C(ortho)-C(ipso)-N-C(imine), project atom indices `[1,0,6,7]`.
- At each nonzero point, all unconstrained Cartesian degrees of freedom are optimized; the requested torsion alone is fixed.

The implementation matches the source's central relaxed-PES energy test but does not claim exact identity to the historical Gaussian 98 SCP/SCNP internal-coordinate restrictions. It is therefore an independent source-aligned reconstruction.

## Energy ledger

At every optimized geometry:

```text
E(theta)  = converged Kohn-Sham total energy
EN(theta) = classical nuclear repulsion
Ee(theta) = E(theta) - EN(theta)
```

All differences are referenced to 0 degrees. The identity `E=Ee+EN` must close within the configured numerical tolerance.

## Primary decision

Let `theta*` be the sampled angle with the lowest total energy. For every ordered interval from 0 degrees through `theta*`, require:

```text
delta Ee < 0
delta EN > 0
delta E  < 0
```

At least two lower-branch intervals are required. A quadratic fit is descriptive support: electronic curvature should be positive and nuclear-repulsion curvature negative. The primary gate uses the actual optimized points, not the fitted curve.

- All technical and directional gates pass: P03 supported for the single parent-NBA tested path.
- Technical gates pass but directional gates are mixed or the minimum is not bracketed: indeterminate; one bounded midpoint may be added.
- Technical gates pass and the opposite direction is consistently observed: P03 opposed in the tested path.

## Boundaries

- No additional molecule, method, basis, solvent, LFMO state or AI model.
- No reuse of P02 correlation or Phase-1 source-defined endpoints as P03 causal evidence.
- No universal claim over all NBA-like species.
- No P08, aromaticity or production-label work.
