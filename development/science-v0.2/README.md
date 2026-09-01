# Science V0.2 development track / 科学增强开发线

This directory is a **development snapshot**, not a new scientific release. It preserves the
Gate V2-0 contracts, machine-readable records, environment identity, final Gate decision, and
separate work-package authorizations for the planned V0.2 evidence-strengthening work. The
frozen V0.1 P01-P14 classifications are not changed by this snapshot.

本目录是**开发快照**，不是新的科学结论版本。它公开 Gate V2-0 合同、机器记录、环境身份、
最终 Gate 判定和独立工作包授权；不会修改 V0.1 已冻结的 P01-P14 十四项结论。

## Current state / 当前状态

```text
GATE_V2_0: PASSED
QP22_CIPSI_ENVIRONMENT: PROVISIONED_AND_NON_CBD_SMOKE_VERIFIED
WP1_CBD_SCIENTIFIC_CALCULATION: AUTHORIZED_TO_START / NOT_STARTED
WP3_HESSIAN_CALCULATION: AUTHORIZED_TO_START / NOT_STARTED
WP2_ORCA_CROSS_PROGRAM: HOLD
WP4_ANNULENE_PILOT: HOLD
SCIENCE_JOBS_STARTED: 0
```

The Quantum Package record covers only an isolated build and official H2/stretched-B2 smoke
fixtures. It is not a cyclobutadiene result, does not validate the WP1 estimand, and does not
upgrade any scientific evidence grade. Gate passage and start authorization are execution
decisions only; they are not new CBD or benzene-mechanism results.

Quantum Package 记录只覆盖隔离构建和官方 H2/拉伸 B2 烟测；它不是环丁二烯结果，不验证
WP1 估计量，也不提升任何科学证据等级。Gate 通过与启动授权只是执行决定，不是新的 CBD
或苯机制科学结果。

## Navigation / 导航

| Path | Purpose |
|---|---|
| [`configs/`](configs/) | Gate state, schemas, estimand registry, frozen anchors and public smoke record |
| [`docs/preregistration/`](docs/preregistration/) | Baseline, blind/audit and resource rules |
| [`docs/protocols/`](docs/protocols/) | WP1-WP4 execution contracts and accepted QP implementation identity |
| [`docs/reports/`](docs/reports/) | WP0 implementation, environment, smoke and specialist-review records |
| [`reproducibility/`](reproducibility/) | Privacy-sanitized Conda environment and explicit package lock |

## Distribution boundary / 分发边界

The repository does not distribute the monograph, Quantum Package source or binaries, raw
scratch/run archives, licensed ORCA software, local host paths, secrets, or WP1/WP3 scientific
inputs. Quantum Package remains governed by its upstream AGPL-3.0 license; this repository only
publishes project-authored metadata, contracts and bounded results.
