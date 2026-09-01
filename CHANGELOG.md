# Changelog

All notable changes to AI4OrgChem public releases are recorded in this file.

## [0.2.0] - 2026-09-01

### Review disposition

- Recorded that the 2026-09-01 third-party AI4OrgChem audit was fixed at `36fdfd4`, while the reported P14 public-evidence gap was closed in PR #8 / `bf0c323`.
- Classified remaining recommendations as closed governance items, explicitly partial environment locking, or future P1 calculations that do not change the frozen 12+2 proposition-level results.

### Added

- Published the four lower-level P14 evidence records, deterministic classification record, and two source-proxy XYZ inputs.
- Added dedicated P14 calculation entry points, a Draft 2020-12 JSON Schema, and a deterministic P14 evidence validator.
- Added a redacted explicit Conda-layer lock for the historical canonical WSL environment.
- Published the self-contained `science-v0.2` package with preregistration, contracts, selected machine results, decisions, reports, rebuild scripts, tests, environment locks, and SHA-256 inventory.
- Added WP1 CBD multireference evidence (`PASS_WITH_METHOD_SENSITIVITY`, P09-B `PARTIALLY_SUPPORTED / R2`) and WP3 benzene mechanism intervention (P10-B `SUPPORTED / R3`).
- Completed the WP2 functional smoke and backend diagnosis: Psi4 1.11 entered a DF backend despite a DIRECT request, exact PK was resource-inappropriate for the largest anchor, and licensed ORCA was unavailable. Gate V2-2 remains `NOT_PASSED`; no eight-anchor completion is claimed.
- Recorded WP4/P12-B as `INDETERMINATE_INPUT_DEFINITION_INCOMPLETE` rather than calculating guessed ISE-II A/B/C/D structures.
- Added deterministic internal clean replay of WP1-WP4 decision/report assembly (`INTERNAL_CLEAN_REPLAY / M1_PLUS`).
- Added CI validation that prevents V0.2 from changing V0.1, overstating WP2/WP4, exposing private host paths, or bundling restricted archives and binaries.

### Changed

- Global JSON validation now rejects duplicate keys and CI rebuilds the P14 decision from lower-level evidence.
- Agent maturity is explicitly M1+ rather than externally replayable M2; P07 is marked `DERIVED` and P12 exact-onset comparison `INCOMPARABLE`.

### Scientific status

- No P01-P14 numerical value or proposition-level classification changed. P14 remains consistent only within the frozen single-C12H6 source-proxy protocol.
- V0.2 strengthens evidence without changing any frozen V0.1 P01-P14 value or proposition-level classification. WP1 and WP3 add completed scientific evidence; WP2 and WP4 retain explicit non-passing outcomes.

## [0.1.2] - 2026-08-28

### Added

- Added GitHub-native discoverability and community-review assets: repository badges, structured issue forms, Discussions entry points, and a social-preview asset.
- Added a bilingual security reporting policy at `.github/SECURITY.md`.

### Security

- Protected `main` with a repository ruleset requiring pull requests, resolved conversations, and the `validate` status check, while retaining zero required human approvals for the single-maintainer workflow.
- Enabled dependency graph, Dependabot alerts and security updates, CodeQL default setup, secret scanning, and push protection.
- Restricted GitHub Actions to CCcolab-owned and GitHub-authored Actions and required immutable full-length commit SHAs.
- Upgraded `actions/checkout` to v5 and `actions/setup-python` to v6 using verified full SHAs, eliminating the Node.js 20 deprecation warning.
- Added release validation that rejects unpinned or unapproved Actions.

### Scientific status

- No P01-P14 scientific value, classification, protocol, or evidence boundary changed from `v0.1.1`.

## [0.1.1] - 2026-08-27

### Added

- Added Chinese and English rapid-review guides that enable quantum-chemistry experts without GitHub, AI, or software-engineering backgrounds to inspect the scientific argument in 10–30 minutes.
- Made Zhong-Heng Yu's authorship of the assessed monograph prominent across project-background and review entry points, and added the public contact email for Xiao Chen.
- Added a clear AI-assistance disclosure for OpenAI Codex (GPT-5.6), while retaining Xiao Chen as the sole project author and scientific-responsibility holder.

### Scientific status

- No P01-P14 scientific value, classification, protocol, or evidence boundary changed from `v0.1.0`.

## [0.1.0] - 2026-08-26

### Released

- promoted the validated private release candidate to the initial curated release;
- confirmed Xiao Chen as the sole author, recorded CRediT contributions, and declared no financial or non-financial competing interests;
- retained the frozen P01-P14 scientific evidence, public software, WSL 2 reproducibility materials, and bounded AI4S engineering results without scientific-value changes.

## [0.1.0-rc3] - 2026-08-26

### Changed

- identified the GitHub release accurately as a private candidate rather than a local, not-yet-uploaded package;
- replaced internal AI work-package identifiers in public project pages with descriptive engineering capabilities;
- retained all P01-P14 scientific values, classifications, evidence boundaries, and public software without change.

## [0.1.0-rc2] - 2026-08-26

### Added

- a detailed WSL 2 computation guide on the GitHub home page, including the verified hardware/software stack, task classes, the P01-P14 determination-entry matrix, job data flow, computation discipline, archive map, reproduction summary, and related documents;
- a safe maintainer command for refreshing the file inventory and SHA-256 snapshot after authorized changes;
- CI enforcement that the detailed guide retains all required sections and exactly fourteen proposition rows.

### Changed

- preserved `v0.1.0-rc1` as an immutable local candidate and advanced the updated home page to `v0.1.0-rc2`;
- clarified that WSL 2 is the canonical validated runtime, not a mathematical requirement of quantum chemistry.

## [0.1.0-rc1] - 2026-08-26

### Added

- scope-bounded classifications and evidence packages for P01-P14;
- English and Chinese manuscripts and the fourteen-proposition evidence matrix;
- project background, research questions, value, achievements, and AI4S Agent documentation;
- public LFMO, conditional-SCF, and independent energy-assembly components;
- one self-contained evidence validator and 64 focused public tests;
- WSL 2 / Ubuntu 24.04 runtime matrices and two shell entry points;
- SHA-256 manifest and file inventory.

### Scientific status

- 12 propositions are consistent or scope-consistent with the corresponding monograph proposition;
- 2 are partially consistent, with the retained differences documented for P11 and P12;
- 0 are globally inconsistent and 0 remain unknown;
- no industrial-scale molecular generalization or universal opposite law is claimed.

### Release status

This release candidate was assembled and validated locally and is preserved as the pre-computation-guide snapshot. It has not been pushed to GitHub or peer reviewed.
