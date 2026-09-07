from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def state(record: dict) -> str | None:
    for key in ("status", "gate_status", "scientific_status", "open_program_lane"):
        if key in record:
            return str(record[key])
    return None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    contract_path = project / "configs/science_v0.3/wp6_release_contract.json"
    contract = load(contract_path)
    records, checks = {}, {}
    for item in contract["prerequisites"]:
        path = project / item["record"]
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {item['work_package']} {path}")
        record = load(path)
        observed = state(record)
        passed = observed in item["accepted"]
        records[item["work_package"]] = {
            "path": item["record"], "sha256": sha(path), "status": observed
        }
        checks[item["work_package"]] = passed
    wp5 = load(project / records["WP5"]["path"])
    checks["WP5_EXTERNAL_CLEAN_REPLAY"] = wp5.get("replay_status") == "EXTERNAL_CLEAN_REPLAY"
    checks["WP5_M2"] = wp5.get("agent_maturity") == "M2"
    if not all(checks.values()):
        raise RuntimeError(f"V0.3 release prerequisites not passed: {checks}")
    status = {
        "schema_version": "science-v0.3-release-status-1",
        "version": "0.3.0",
        "status": "RELEASE_PACKAGE_AUTHORIZED_NOT_YET_BUILT",
        "release_date": str(date.today()),
        "v0_1_v0_2_mutated": False,
        "checks": checks,
        "records": records,
        "scientific_scope_statement": "V0.3 closes the seven preregistered enhancement tasks; evidence relations and estimator boundaries remain explicit and no claim is generalized beyond the tested domains.",
        "local_package_review": "AUTHORIZED_NOT_YET_BUILT",
        "remote_tag_created": False,
        "github_release_created": False,
        "post_tag_clean_clone_verified": False,
    }
    output = project / "configs/science_v0.3/v0.3_release_status.json"
    output.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    release_dir = project / "docs/releases/science_v0.3"
    release_dir.mkdir(parents=True, exist_ok=True)
    wp4b_summary = load(project / "data/science_v0.3/processed/wp4b/wp4b_paired_pilot_summary.json")
    points = "\n".join(
        f"| {row['N']} | {row['series']} | {float(row['e0_ase_kcal_mol']):.6f} | {row['classification']} |"
        for row in wp4b_summary["six_point_results"]
    )
    notes = f"""# AI4OrgChem V0.3.0 scientific-closure release

V0.3.0 completes the seven frozen enhancement tasks in their registered order. It adds evidence without changing the immutable V0.1.0 or V0.2.0 releases.

| Order | Work package | Final state |
|---:|---|---|
| 1 | WP1 cyclobutadiene multireference anchor | `{records['WP1']['status']}` |
| 2 | WP2 open three-program reproduction | `{records['WP2']['status']}` |
| 3 | WP3 benzene D6h mechanism | `{records['WP3']['status']}`; P10-A R2 and P10-B R3 remain separate |
| 4 | WP4-A source-aligned CESE | `{records['WP4-A']['status']}` / R1 |
| 5 | WP4-B physical-state 0 K ASE | `{records['WP4-B']['status']}` |
| 6 | WP5 independent Agent replay | `{wp5['replay_status']} / {wp5['agent_maturity']}` |
| 7 | WP6 package | local release package ready; remote tag/release pending |

## WP4-B paired pilot

| N | series | 0 K ASE (kcal/mol) | registered classification |
|---:|---|---:|---|
{points}

WP4-A and WP4-B remain different estimands and are not averaged or used to overwrite one another. Agent replay status is independent of scientific grades R1-R3. No conclusion is generalized outside the tested systems.

## Reproducibility anchors

- WP2: 8/8 absolute-energy/gradient anchors and 2/2 relative-energy pairs passed across PySCF, Psi4, and NWChem in the frozen open three-program estimand. The unavailable ORCA-specific lane remains explicitly unexecuted.
- WP5: an external Agent replay in a clean, bundle-only environment reproduced the frozen energy within `{wp5['absolute_difference_hartree']:.3e} Eh`; replay maturity is `{wp5['agent_maturity']}` and does not change R1-R3 scientific grades.
- WP6: the local staged package, SHA-256 manifest, credential/private-path scan, forbidden-material scan, and final validator pass. The final Git commit, remote `v0.3.0` tag, GitHub Release, and post-tag clean-clone verification remain publication actions rather than completed local checks.

## Known boundaries and recovered failures

- WP1 supports the tested sign but retains large method sensitivity; it is not a method-independent quantitative barrier.
- WP4-B is a six-point paired pilot, not a complete annulene-size law. `N=10` is boundary-sensitive under the registered ±2 kcal/mol rule, and the `N=32/A` broken-symmetry solution does not change the registered `N=32` classification.
- Parallel large-annulene work encountered memory pressure and was recovered by bounded serial execution. Two release-interface field mismatches and a self-scan false positive were repaired without recalculating or changing scientific values.
- V0.3.0 does not alter the P01-P14 classification matrix, does not claim industrial-scale ML generalization, has not undergone peer review, and is not an institutional or model-provider certification of the monograph.

## Publication state

Local status: `RELEASE_PACKAGE_READY`. Remote publication identifiers are intentionally pending until the final reviewed commit is fixed. See `reports/V0.3_PRE_RELEASE_REVIEW.md` and `sha256-manifest.json` in the staged package.

## 中文说明

V0.3.0 按冻结顺序闭合七项增强任务，只新增证据，不改写不可变的 V0.1.0、V0.2.0，也不改变P01-P14既有分类。WP4-A 的原著 CESE 同估计量支路与 WP4-B 的物理态 0 K ASE 支路继续隔离，不平均、不互相覆盖；WP5 的 Agent 重放成熟度不自动提高 R1-R3 科学等级；任何结论均不外推到受测体系之外。当前本地发布包已通过校验，最终提交哈希、远程`v0.3.0`标签、GitHub Release及标签后洁净克隆复验仍待发布阶段完成。
"""
    (release_dir / "V0.3_RELEASE_NOTES.md").write_text(
        notes, encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
