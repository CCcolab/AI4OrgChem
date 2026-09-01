from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/science_v0.2/claim_estimand_registry.json"
CONTRACT = ROOT / "docs/releases/science_v0.2/protocols/WP1_WP4_EXECUTION_CONTRACTS.md"
OUT_DIR = ROOT / "data/science_v0.2/decisions/wp4"
REPORT = ROOT / "docs/releases/science_v0.2/reports/WP4_GATE_V2_4P_REPORT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    p12b = next(row for row in registry["records"] if row["claim_id"] == "P12-B")
    required = {
        "paired_N": [8, 10, 16, 18, 32, 34],
        "species_per_N": ["A", "B", "C", "D"],
        "cartesian_coordinates": True,
        "two_independent_conformer_sources": True,
        "frequency_verified_minima": True,
        "zpe_corrected_energies": True,
        "closed_shell_and_broken_symmetry_for_4n": True,
    }
    input_candidates = list((ROOT / "data/science_v0.2/inputs/wp4").glob("**/*")) if (ROOT / "data/science_v0.2/inputs/wp4").exists() else []
    geometry_files = [p for p in input_candidates if p.is_file() and p.suffix.lower() in {".xyz", ".sdf", ".mol", ".json"}]
    complete_input = False
    decision = {
        "schema_version": "science-v0.2-wp4-decision-1",
        "work_package": "WP4",
        "gate": "V2-4P",
        "gate_status": "NOT_PASSED",
        "scientific_status": "INDETERMINATE_INPUT_DEFINITION_INCOMPLETE",
        "scientific_calculation_started": False,
        "required_input_contract": required,
        "candidate_input_files_found": [str(p.relative_to(ROOT)).replace("\\", "/") for p in geometry_files],
        "complete_frozen_A_B_C_D_set_present": complete_input,
        "estimand": p12b["estimand_id"],
        "relation_to_p12_a": "INCOMPARABLE",
        "v0_1_p12_a_changed": False,
        "reason": "The frozen protocol names the ISE-II species roles but the repository does not contain exact, versioned A/B/C/D identities and Cartesian conformer sets for all six paired N values. Running guessed structures would change the estimand.",
        "external_definition_note": "The 2025 source states that B/D electronic energies and ZPVE are inherited from an earlier reference, so the present repository cannot reconstruct the complete reaction solely from the high-level description.",
        "registry_sha256": sha(REGISTRY),
        "contract_sha256": sha(CONTRACT),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "gate_v2_4p_decision.json"
    path.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# WP4 / Gate V2-4P 轮烯成对先导报告\n\n"
        "- Gate：`NOT_PASSED`\n"
        "- 科学状态：`INDETERMINATE_INPUT_DEFINITION_INCOMPLETE`\n"
        "- 科学计算：未启动，避免以猜测结构改变 ISE-II 估计量\n"
        "- P12-A：V0.1 冻结结论不变\n"
        "- P12-A / P12-B：`INCOMPARABLE`\n\n"
        "## 原因\n\n"
        "协议已冻结 `8/10、16/18、32/34`、B3LYP/6-31G(d)、ZPVE、双构象来源和停止标准，但本地尚无六组 A/B/C/D 的精确结构身份与笛卡尔坐标。2025 年 ISE-II 来源还复用了更早文献中的 B/D 能量和 ZPVE。此时直接生成结构会改变主估计量，因此本次 V0.2 将缺口作为可审计结果发布，而不制造数值。\n\n"
        "来源核对：[Van Nyvel, Alonso and Solà, Chemical Science 2025, DOI 10.1039/D4SC08225G](https://doi.org/10.1039/D4SC08225G) 及其补充信息。\n\n"
        "## 后续解锁条件\n\n"
        "取得并许可归档 A/B/C/D 的来源结构、版本化坐标及反–顺校正定义后，重新密封 WP4 输入包，再执行构象搜索、无虚频确认和 0 K ASE。\n",
        encoding="utf-8",
    )
    print(json.dumps({"gate_status": decision["gate_status"], "scientific_status": decision["scientific_status"]}, indent=2))


if __name__ == "__main__":
    main()
