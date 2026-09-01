from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/science_v0.2/raw/wp2/wp2_open_program_anchors.json"
DECISION_DIR = ROOT / "data/science_v0.2/decisions/wp2"
REPORT = ROOT / "docs/releases/science_v0.2/reports/WP2_GATE_V2_2_REPORT.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    open_pass = bool(raw["open_program_lane_pass"])
    backend_pass = bool(raw.get("backend_contract", {}).get("pass", True))
    orca = bool(raw["programs"]["ORCA_available"])
    gate_pass = open_pass and orca and bool(raw["three_program_core_contract_pass"])
    if gate_pass:
        status = "PASSED"
    elif not backend_pass:
        status = "INDETERMINATE_PSI4_BACKEND_CONTRACT_AND_ORCA_UNAVAILABLE"
    elif not open_pass:
        status = "INDETERMINATE_OPEN_PROGRAM_ALIGNMENT_FAILED"
    else:
        status = "INDETERMINATE_ORCA_UNAVAILABLE"
    decision = {
        "schema_version": "science-v0.2-wp2-decision-1",
        "work_package": "WP2",
        "gate": "V2-2",
        "gate_status": "PASS" if gate_pass else "NOT_PASSED",
        "scientific_status": status,
        "open_program_lane": "PASS" if open_pass else "FAIL",
        "psi4_backend_contract": "PASS" if backend_pass else "FAIL",
        "three_program_core_lane": "PASS" if gate_pass else "NOT_ESTABLISHED",
        "orca_available": orca,
        "orca_substitute_used": False,
        "v0_1_claims_changed": False,
        "relation_to_v0_1_claims": "COMPLEMENTARY",
        "raw_result": str(RAW.relative_to(ROOT)).replace("\\", "/"),
        "raw_sha256": digest(RAW),
        "limitations": [
            "PySCF/Psi4 ordinary-state agreement cannot be relabeled as a clean-room reconstruction of custom LFMO/DSI/FUD states.",
            "The preregistered three-program core requires licensed ORCA results for every anchor.",
            "The P03 constrained-dihedral observable is implemented as a deterministic rigid-fragment tangent projection on the frozen source axis, not as a program-specific optimizer Lagrange multiplier.",
        ],
    }
    DECISION_DIR.mkdir(parents=True, exist_ok=True)
    out = DECISION_DIR / "gate_v2_2_decision.json"
    out.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    max_e = max((row["comparison"]["absolute_energy_difference_hartree"] for row in raw["anchors"]), default=float("nan"))
    gradients = [row["comparison"]["gradient_rms_difference_hartree_per_bohr"] for row in raw["anchors"] if "gradient_rms_difference_hartree_per_bohr" in row["comparison"]]
    lines = [
        "# WP2 / Gate V2-2 跨程序复算报告",
        "",
        f"- Gate：`{decision['gate_status']}`",
        f"- 科学状态：`{status}`",
        f"- PySCF/Psi4 功能能量烟测：`{'PASS' if raw.get('functional_energy_alignment_smoke_pass', open_pass) else 'FAIL'}`",
        f"- Psi4 无DF后端合同：`{'PASS' if backend_pass else 'FAIL'}`",
        f"- ORCA：`{'available' if orca else 'not available'}`；未使用替代程序冒充 ORCA",
        f"- 烟测/锚点最大绝对能量差：`{max_e if raw['anchors'] else raw.get('functional_energy_alignment_absolute_difference_hartree', float('nan')):.12g} Eh`（门限 `5e-6 Eh`）",
        f"- 最大梯度 RMS 差：`{max(gradients) if gradients else float('nan'):.12g} Eh/bohr`（门限 `5e-5 Eh/bohr`）",
        "",
        "## 判定",
        "",
        "苯功能能量烟测在数值容差内，但Psi4 1.11在请求DIRECT DFT时实际进入MemDFJK/@DF-RKS；精确PK路径对最大NBA锚点又超出本轮合理资源规模。因此八个核心锚点在第一个结果产生前按失败纪律停止。加之本机没有经许可的ORCA二进制，Gate V2-2保持NOT_PASSED。该结果不修改V0.1十四项结论，也不把普通态复算冒充LFMO/DSI/FUD自定义态复现。",
        "",
        f"机器记录：`{decision['raw_result']}`（SHA-256 `{decision['raw_sha256']}`）。",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"gate_status": decision["gate_status"], "scientific_status": status}, indent=2))


if __name__ == "__main__":
    main()
