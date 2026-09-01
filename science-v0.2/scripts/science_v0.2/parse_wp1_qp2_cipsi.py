#!/usr/bin/env python3
"""Parse the frozen WP1 Quantum Package endpoint runs into an auditable JSON ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_scalar(path: Path) -> float | int:
    text = path.read_text(encoding="utf-8", errors="replace").strip().replace("D", "E")
    match = re.search(FLOAT, text)
    if not match:
        raise ValueError(f"no numeric scalar in {path}")
    value = float(match.group(0))
    return int(value) if path.name == "n_det.txt" else value


def iteration_series(text: str) -> list[dict[str, float | int | None]]:
    """Extract conservative CIPSI iteration records across QP 2.2.x text variants."""
    summary_rows: list[dict[str, float | int | None]] = []
    starts = list(re.finditer(r"Summary at N_det\s*=\s*(\d+)", text))
    for index, match in enumerate(starts):
        block = text[match.start() : starts[index + 1].start() if index + 1 < len(starts) else len(text)]
        e_match = re.search(rf"^# E\s+({FLOAT})\s*$", block, re.M)
        pt2_match = re.search(rf"^# PT2\s+({FLOAT})\s+({FLOAT})\s*$", block, re.M)
        variance_match = re.search(rf"^\s*Variance\s*=\s*({FLOAT})\s*\+/-\s*({FLOAT})", block, re.M)
        extrapolated = re.findall(rf"^\s*({FLOAT})\s+({FLOAT})\s*$", block, re.M)
        if e_match and pt2_match:
            e_var = float(e_match.group(1).replace("D", "E"))
            e_pt2 = float(pt2_match.group(1).replace("D", "E"))
            summary_rows.append({
                "n_det": int(match.group(1)),
                "e_var_hartree": e_var,
                "e_pt2_hartree": e_pt2,
                "e_var_plus_pt2_hartree": e_var + e_pt2,
                "pt2_statistical_error_hartree": float(pt2_match.group(2).replace("D", "E")),
                "variance_hartree2": float(variance_match.group(1).replace("D", "E")) if variance_match else None,
                "variance_statistical_error_hartree2": float(variance_match.group(2).replace("D", "E")) if variance_match else None,
                "fci_extrapolation_points": [
                    {"minimum_pt2_hartree": float(a.replace("D", "E")), "extrapolated_energy_hartree": float(b.replace("D", "E"))}
                    for a, b in extrapolated
                ],
            })
    if summary_rows:
        return summary_rows

    rows: list[dict[str, float | int | None]] = []
    n_det: int | None = None
    e_var: float | None = None
    e_pt2: float | None = None
    pt2_error: float | None = None
    variance: float | None = None

    def emit() -> None:
        nonlocal n_det, e_var, e_pt2, pt2_error, variance
        if n_det is not None and e_var is not None and e_pt2 is not None:
            candidate = {
                "n_det": n_det,
                "e_var_hartree": e_var,
                "e_pt2_hartree": e_pt2,
                "e_var_plus_pt2_hartree": e_var + e_pt2,
                "pt2_statistical_error_hartree": pt2_error,
                "variance_hartree2": variance,
            }
            if not rows or candidate != rows[-1]:
                rows.append(candidate)

    for line in text.splitlines():
        lower = line.lower()
        m = re.search(r"n[_ ]?det\s*(?:=|:)\s*(\d+)", lower)
        if m:
            emit()
            n_det = int(m.group(1))
            e_var = e_pt2 = pt2_error = variance = None
        m = re.search(rf"(?:e[_ ]?var|energy)\s*(?:=|:)\s*({FLOAT})", line, re.I)
        if m and "pt2" not in lower:
            e_var = float(m.group(1).replace("D", "E"))
        m = re.search(rf"(?:pt2(?: energy)?|e[_ ]?pt2)\s*(?:=|:)\s*({FLOAT})(?:\s*\+/-\s*({FLOAT}))?", line, re.I)
        if m:
            e_pt2 = float(m.group(1).replace("D", "E"))
            if m.group(2):
                pt2_error = float(m.group(2).replace("D", "E"))
        m = re.search(rf"variance\s*(?:=|:)\s*({FLOAT})", line, re.I)
        if m:
            variance = float(m.group(1).replace("D", "E"))
        if n_det is not None and e_var is not None and e_pt2 is not None:
            emit()
    emit()
    return rows


def endpoint_record(root: Path, endpoint: str) -> dict:
    folder = root / endpoint
    required = [
        "create_ezfio.log", "scf.log", "frozen_core.log", "cipsi.log",
        "hf_energy.txt", "variational_energy.txt",
        "variational_plus_pt2_energy.txt", "n_det.txt",
    ]
    missing = [name for name in required if not (folder / name).is_file()]
    if missing:
        return {"endpoint": endpoint.upper(), "status": "FAIL_INCOMPLETE", "missing": missing}
    cipsi_log = folder / "cipsi.log"
    series = iteration_series(cipsi_log.read_text(encoding="utf-8", errors="replace"))
    artifacts = [{"path": str((folder / name).relative_to(root)), "sha256": sha256(folder / name)} for name in required]
    return {
        "endpoint": endpoint.upper(),
        "status": "PASS",
        "hf_energy_hartree": read_scalar(folder / "hf_energy.txt"),
        "e_var_hartree": read_scalar(folder / "variational_energy.txt"),
        "e_var_plus_pt2_hartree": read_scalar(folder / "variational_plus_pt2_energy.txt"),
        "n_det": read_scalar(folder / "n_det.txt"),
        "iteration_series": series,
        "iteration_series_parse_status": "PASS" if series else "NOT_EXTRACTED_LOG_RETAINED",
        "artifacts": artifacts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = [endpoint_record(args.run_root, name) for name in ("d2h", "d4h")]
    payload = {
        "schema_version": "science-v0.2-wp1-qp2-cipsi-result-1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "work_package": "WP1",
        "role": "PRIMARY_HIGH_LEVEL_ANCHOR",
        "implementation": "Quantum Package v2.2.2 CIPSI+PT2",
        "run_root": str(args.run_root),
        "status": "PASS" if all(row["status"] == "PASS" for row in records) else "FAIL_INCOMPLETE",
        "endpoints": records,
        "interpretation_boundary": "Ordinary physical-state anchor for P09-B; it is COMPLEMENTARY to, and does not automatically upgrade, the P09-A conditional-state estimand.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
