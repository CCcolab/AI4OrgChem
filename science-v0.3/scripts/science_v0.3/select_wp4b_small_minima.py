from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--n-values", default="8,10,16,18,32,34")
    parser.add_argument("--secondary-sources", default="etkdg,auditbest,crest")
    args = parser.parse_args()
    n_values = tuple(int(value) for value in args.n_values.split(",") if value.strip())
    if not set(n_values) <= {8, 10, 16, 18, 32, 34}:
        raise ValueError("N is outside the frozen WP4-B paired pilot")
    secondary_sources = tuple(value.strip() for value in args.secondary_sources.split(",") if value.strip())
    if not set(secondary_sources) <= {"etkdg", "auditbest", "crest"}:
        raise ValueError("Unsupported secondary source")
    audit_path = args.project / "data/science_v0.3/raw/wp4b/etkdg_discovery_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {"records": []}
    crest_required = {
        (int(row["N"]), str(row["species"]))
        for row in audit.get("records", [])
        if not row.get("final_four_no_new_unique_within_window", False)
    }
    raw = args.project / "data/science_v0.3/raw/wp4b"
    anchors_path = args.project / "configs/science_v0.3/wp4b_source_0k_anchors.json"
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    anchor_by_key = {
        (int(row["N"]), str(row["species"])): row
        for row in anchors["records"]
    }
    rows: list[dict[str, object]] = []
    missing: list[str] = []
    selected: list[dict[str, object]] = []
    for n in n_values:
        for species in "ABCD":
            candidates: list[dict[str, object]] = []
            # Every registered deterministic ETKDG candidate must compete at
            # the final QM level.  ``auditbest`` is an additional member of
            # the ETKDG source family, not a replacement for the original
            # seeded candidate.  CREST is required only for identities whose
            # preregistered ETKDG stopping rule failed at 32 attempts.
            required_sources = ["source"]
            required_sources.extend(source for source in secondary_sources if source != "crest")
            if "crest" in secondary_sources and (n, species) in crest_required:
                required_sources.append("crest")
            required_sources = list(dict.fromkeys(required_sources))
            for source in required_sources:
                job_id = f"N{n:02d}_{species}_{source}"
                path = raw / f"{job_id}.json"
                if source == "source" and (n, species) in anchor_by_key and not path.exists():
                    anchor = anchor_by_key[(n, species)]
                    candidates.append({
                        "id": job_id,
                        "source": source,
                        "electronic_hartree": float(anchor["electronic_hartree"]),
                        "scf_converged": True,
                        "optimization_converged": True,
                        "schema_version": "published-source-anchor-1",
                        "e0_hartree": float(anchor["e0_hartree"]),
                    })
                    continue
                if not path.exists():
                    missing.append(job_id)
                    continue
                data = json.loads(path.read_text(encoding="utf-8"))
                candidates.append({
                    "id": job_id,
                    "source": source,
                    "electronic_hartree": float(data["electronic_hartree"]),
                    "scf_converged": bool(data["scf_converged"]),
                    "optimization_converged": bool(data["optimization_converged"]),
                    "schema_version": data["schema_version"],
                })
            if len(candidates) == len(required_sources):
                winner = min(candidates, key=lambda row: float(row["electronic_hartree"]))
                ordered = sorted(candidates, key=lambda row: float(row["electronic_hartree"]))
                gap = (
                    (float(ordered[1]["electronic_hartree"]) - float(ordered[0]["electronic_hartree"]))
                    * 627.5094740631
                    if len(ordered) > 1
                    else None
                )
                selection = {
                    "N": n,
                    "species": species,
                    "selected_id": winner["id"],
                    "selection_metric": "lowest final electronic energy; published source anchor competes with final PySCF candidates for N>=16",
                    "candidate_gap_kcal_mol": gap,
                    "candidates": candidates,
                }
                rows.append(selection)
                selected.append({"N": n, "species": species, "id": winner["id"]})
    result = {
        "schema_version": "science-v0.3-wp4b-paired-selection-2",
        "n_values": list(n_values),
        "secondary_sources": list(secondary_sources),
        "crest_required": [{"N": n, "species": species} for n, species in sorted(crest_required)],
        "complete": len(missing) == 0 and len(selected) == len(n_values) * 4,
        "missing": missing,
        "selections": rows,
        "selected": selected,
    }
    output = raw / ("small_conformer_selection.json" if set(n_values) == {8, 10} else "paired_conformer_selection.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
