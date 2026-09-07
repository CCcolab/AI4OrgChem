from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign


def xyz_text(mol: Chem.Mol, comment: str) -> str:
    conf = mol.GetConformer()
    lines = [str(mol.GetNumAtoms()), comment]
    for atom in mol.GetAtoms():
        point = conf.GetAtomPosition(atom.GetIdx())
        lines.append(f"{atom.GetSymbol():2s} {point.x: .10f} {point.y: .10f} {point.z: .10f}")
    return "\n".join(lines) + "\n"


def optimize_candidate(smiles: str, seed: int) -> tuple[Chem.Mol | None, float | None, str]:
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.pruneRmsThresh = -1.0
    params.numThreads = 1
    if AllChem.EmbedMolecule(mol, params) < 0:
        return None, None, "EMBED_FAILED"
    props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
    if props is not None:
        AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
        ff = AllChem.MMFFGetMoleculeForceField(mol, props)
        method = "MMFF94s"
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
        ff = AllChem.UFFGetMoleculeForceField(mol)
        method = "UFF"
    return mol, float(ff.CalcEnergy()), method


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--prune-rms", type=float, default=0.50)
    parser.add_argument("--window-kcal", type=float, default=1.0)
    args = parser.parse_args()
    manifest_path = args.project / "data/science_v0.3/inputs/wp4b/input_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records: list[dict[str, object]] = []
    started = time.perf_counter()
    for row in manifest["records"]:
        n = int(row["N"])
        species = str(row["species"])
        accepted: list[tuple[int, Chem.Mol, float]] = []
        attempts: list[dict[str, object]] = []
        for attempt_index in range(1, args.attempts + 1):
            seed = 970000 + n * 100 + ord(species) * 10 + attempt_index
            mol, energy, method = optimize_candidate(row["canonical_smiles"], seed)
            if mol is None or energy is None:
                attempts.append({"attempt": attempt_index, "seed": seed, "status": method})
                continue
            heavy = Chem.RemoveHs(mol)
            rms_values = [
                float(rdMolAlign.GetBestRMS(heavy, Chem.RemoveHs(previous)))
                for _, previous, _ in accepted
            ]
            unique = not rms_values or min(rms_values) >= args.prune_rms
            if unique:
                accepted.append((attempt_index, mol, energy))
            attempts.append({
                "attempt": attempt_index,
                "seed": seed,
                "status": "OPTIMIZED",
                "method": method,
                "prescreen_energy_kcal_mol": energy,
                "minimum_heavy_atom_rms_to_previous_angstrom": min(rms_values) if rms_values else None,
                "unique_at_preregistered_rms": unique,
            })
        energies = [energy for _, _, energy in accepted]
        best = min(energies) if energies else None
        best_path = None
        best_sha256 = None
        if accepted:
            best_index, best_mol, best = min(accepted, key=lambda item: item[2])
            best_path_obj = args.project / f"data/science_v0.3/inputs/wp4b/N{n:02d}_{species}_auditbest.xyz"
            best_path_obj.write_text(
                xyz_text(best_mol, f"WP4-B deterministic ETKDG discovery-audit best; attempt={best_index}; prescreen_energy={best:.12f}"),
                encoding="utf-8",
            )
            best_path = str(best_path_obj.relative_to(args.project)).replace("\\", "/")
            best_sha256 = hashlib.sha256(best_path_obj.read_bytes()).hexdigest()
        late_low_unique = [
            index
            for index, _, energy in accepted
            if index > args.attempts - 4 and best is not None and energy <= best + args.window_kcal
        ]
        records.append({
            "N": n,
            "species": species,
            "attempt_count": args.attempts,
            "optimized_count": sum(item["status"] == "OPTIMIZED" for item in attempts),
            "unique_count": len(accepted),
            "best_prescreen_energy_kcal_mol": best,
            "best_candidate_path": best_path,
            "best_candidate_sha256": best_sha256,
            "late_low_unique_attempts": late_low_unique,
            "final_four_no_new_unique_within_window": len(late_low_unique) == 0,
            "attempts": attempts,
        })
    result = {
        "schema_version": "science-v0.3-wp4b-etkdg-discovery-audit-1",
        "attempts_per_system": args.attempts,
        "prune_rms_angstrom": args.prune_rms,
        "near_degenerate_window_kcal_mol": args.window_kcal,
        "records": records,
        "all_systems_stop_rule_pass": all(row["final_four_no_new_unique_within_window"] for row in records),
        "elapsed_seconds": time.perf_counter() - started,
        "scope": "Independent deterministic ETKDG discovery audit; prescreen evidence only, not a quantum-chemistry label.",
    }
    output = args.project / "data/science_v0.3/raw/wp4b/etkdg_discovery_audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "all_systems_stop_rule_pass": result["all_systems_stop_rule_pass"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
