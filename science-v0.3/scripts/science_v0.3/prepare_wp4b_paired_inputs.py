from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdDetermineBonds, rdMolDescriptors, rdMolTransforms


PAIRED_N = (8, 10, 16, 18, 32, 34)
SPECIES = "ABCD"
PUBLISHED_N = (16, 18, 32, 34)
ARCHIVE_MD5 = "cd7c7bde08e17b93536da49fda597807"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clear_stereo(mol: Chem.Mol) -> None:
    for bond in mol.GetBonds():
        bond.SetStereo(Chem.BondStereo.STEREONONE)
        bond.SetBondDir(Chem.BondDir.NONE)
    for atom in mol.GetAtoms():
        atom.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)


def mol_from_xyz(path: Path) -> Chem.Mol:
    mol = Chem.MolFromXYZFile(str(path))
    if mol is None:
        raise ValueError(f"Cannot parse XYZ: {path}")
    rdDetermineBonds.DetermineBonds(mol, charge=0)
    return mol


def ring_sizes(mol: Chem.Mol) -> list[int]:
    return sorted(len(ring) for ring in Chem.GetSymmSSSR(Chem.RemoveHs(mol)))


def contract_c2h2_once(mol: Chem.Mol) -> Chem.Mol:
    heavy = Chem.RemoveHs(Chem.Mol(mol))
    clear_stereo(heavy)
    Chem.Kekulize(heavy, clearAromaticFlags=True)
    rings = [list(ring) for ring in Chem.GetSymmSSSR(heavy)]
    large = max(rings, key=len)
    small = set(min(rings, key=len))
    fused = {a.GetIdx() for a in heavy.GetAtoms() if a.GetDegree() == 3}
    candidates: list[tuple[int, int, int, int, int]] = []
    for pos in range(len(large)):
        p, a, b, q = [large[(pos + offset) % len(large)] for offset in range(4)]
        if a in fused or b in fused or a in small or b in small:
            continue
        if heavy.GetAtomWithIdx(a).GetTotalNumHs() != 1 or heavy.GetAtomWithIdx(b).GetTotalNumHs() != 1:
            continue
        bonds = (
            heavy.GetBondBetweenAtoms(p, a).GetBondType(),
            heavy.GetBondBetweenAtoms(a, b).GetBondType(),
            heavy.GetBondBetweenAtoms(b, q).GetBondType(),
        )
        if bonds != (Chem.BondType.SINGLE, Chem.BondType.DOUBLE, Chem.BondType.SINGLE):
            continue
        remoteness = sum(
            min(len(Chem.rdmolops.GetShortestPath(heavy, node, f)) for f in fused)
            for node in (a, b)
        )
        candidates.append((remoteness, p, a, b, q))
    if not candidates:
        raise RuntimeError("No admissible remote S-D-S C2H2 contraction was found")
    _, p, a, b, q = max(candidates)
    rw = Chem.RWMol(heavy)
    for idx in sorted((a, b), reverse=True):
        rw.RemoveAtom(idx)

    def shifted(old: int) -> int:
        return old - int(old > a) - int(old > b)

    rw.AddBond(shifted(p), shifted(q), Chem.BondType.SINGLE)
    result = rw.GetMol()
    clear_stereo(result)
    Chem.SanitizeMol(result)
    return result


def graph_for_small_n(parent: Chem.Mol, target_n: int) -> Chem.Mol:
    mol = Chem.RemoveHs(Chem.Mol(parent))
    current_n = max(ring_sizes(mol))
    while current_n > target_n:
        mol = contract_c2h2_once(mol)
        current_n = max(ring_sizes(mol))
    if current_n != target_n:
        raise ValueError(f"Contraction ended at N={current_n}, expected {target_n}")
    return mol


def embed_candidates(heavy: Chem.Mol, seed: int, attempts: int) -> list[tuple[Chem.Mol, float, str]]:
    mol = Chem.AddHs(Chem.Mol(heavy))
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.pruneRmsThresh = 0.50
    params.numThreads = 0
    conf_ids = list(AllChem.EmbedMultipleConfs(mol, numConfs=attempts, params=params))
    results: list[tuple[Chem.Mol, float, str]] = []
    for cid in conf_ids:
        candidate = Chem.Mol(mol)
        keep = Chem.Conformer(candidate.GetConformer(cid))
        candidate.RemoveAllConformers()
        candidate.AddConformer(keep, assignId=True)
        method = "MMFF94s"
        props = AllChem.MMFFGetMoleculeProperties(candidate, mmffVariant="MMFF94s")
        if props is not None:
            AllChem.MMFFOptimizeMolecule(candidate, mmffVariant="MMFF94s", maxIters=2000)
            ff = AllChem.MMFFGetMoleculeForceField(candidate, props)
        else:
            method = "UFF"
            AllChem.UFFOptimizeMolecule(candidate, maxIters=2000)
            ff = AllChem.UFFGetMoleculeForceField(candidate)
        results.append((candidate, float(ff.CalcEnergy()), method))
    return sorted(results, key=lambda item: item[1])


def contracted_parent_candidate(parent: Chem.Mol, target_n: int) -> tuple[Chem.Mol, float, str]:
    heavy = graph_for_small_n(parent, target_n)
    params = AllChem.ETKDGv3()
    params.randomSeed = 91000 + target_n
    params.useRandomCoords = False
    mol = Chem.AddHs(heavy)
    if AllChem.EmbedMolecule(mol, params) < 0:
        params.useRandomCoords = True
        if AllChem.EmbedMolecule(mol, params) < 0:
            raise RuntimeError(f"Failed to embed contracted-parent candidate for N={target_n}")
    props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
    if props is not None:
        AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=4000)
        ff = AllChem.MMFFGetMoleculeForceField(mol, props)
        method = "parent_graph_contraction+MMFF94s"
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=4000)
        ff = AllChem.UFFGetMoleculeForceField(mol)
        method = "parent_graph_contraction+UFF"
    return mol, float(ff.CalcEnergy()), method


def xyz_text(mol: Chem.Mol, comment: str) -> str:
    conf = mol.GetConformer()
    lines = [str(mol.GetNumAtoms()), comment]
    for atom in mol.GetAtoms():
        point = conf.GetAtomPosition(atom.GetIdx())
        lines.append(f"{atom.GetSymbol():2s} {point.x: .10f} {point.y: .10f} {point.z: .10f}")
    return "\n".join(lines) + "\n"


def ez_sequence(mol: Chem.Mol) -> list[dict[str, object]]:
    heavy = Chem.RemoveHs(Chem.Mol(mol))
    clear_stereo(heavy)
    Chem.Kekulize(heavy, clearAromaticFlags=True)
    Chem.AssignStereochemistryFrom3D(heavy)
    rings = [list(ring) for ring in Chem.GetSymmSSSR(heavy)]
    large = max(rings, key=len)
    ring_set = set(large)
    conf = heavy.GetConformer()
    records: list[dict[str, object]] = []
    for bond in heavy.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if i not in ring_set or j not in ring_set:
            continue
        left = [a.GetIdx() for a in heavy.GetAtomWithIdx(i).GetNeighbors() if a.GetIdx() in ring_set and a.GetIdx() != j]
        right = [a.GetIdx() for a in heavy.GetAtomWithIdx(j).GetNeighbors() if a.GetIdx() in ring_set and a.GetIdx() != i]
        if not left or not right:
            continue
        angle = float(rdMolTransforms.GetDihedralDeg(conf, left[0], i, j, right[0]))
        records.append({
            "bond": [i, j],
            "torsion_deg": round(angle, 6),
            "geometry_label": "E" if abs(angle) >= 90.0 else "Z",
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=8)
    args = parser.parse_args()
    started = time.perf_counter()
    if hashlib.md5(args.archive.read_bytes()).hexdigest() != ARCHIVE_MD5:
        raise ValueError("Published coordinate archive MD5 does not match the frozen contract")
    args.output_root.mkdir(parents=True, exist_ok=True)
    parents = {
        species: mol_from_xyz(args.source_root / species / f"{species}12_Singlet_neutral_without_constraints.xyz")
        for species in SPECIES
    }
    manifest: dict[str, object] = {
        "schema_version": "science-v0.3-wp4b-input-manifest-1",
        "archive_md5": ARCHIVE_MD5,
        "paired_N": list(PAIRED_N),
        "records": [],
    }
    records: list[dict[str, object]] = manifest["records"]  # type: ignore[assignment]
    for n in PAIRED_N:
        for species_index, species in enumerate(SPECIES):
            if n in PUBLISHED_N:
                source_path = args.source_root / species / f"{species}{n}_Singlet_neutral_without_constraints.xyz"
                source_mol = mol_from_xyz(source_path)
                primary_mol = source_mol
                primary_method = "published_B3LYP_6-31Gd_unconstrained"
                source_sha = sha256(source_path)
            else:
                primary_mol, _, primary_method = contracted_parent_candidate(parents[species], n)
                source_path = args.source_root / species / f"{species}12_Singlet_neutral_without_constraints.xyz"
                source_sha = sha256(source_path)
            primary_name = f"N{n:02d}_{species}_source.xyz"
            primary_out = args.output_root / primary_name
            primary_out.write_text(
                xyz_text(primary_mol, f"WP4-B {primary_method}; parent_sha256={source_sha}"),
                encoding="utf-8",
            )
            heavy = Chem.RemoveHs(primary_mol)
            secondary = embed_candidates(
                heavy,
                seed=93000 + n * 10 + species_index,
                attempts=args.attempts,
            )
            if not secondary:
                raise RuntimeError(f"No ETKDG candidates for N={n}, species={species}")
            secondary_mol, secondary_energy, secondary_method = secondary[0]
            secondary_name = f"N{n:02d}_{species}_etkdg.xyz"
            secondary_out = args.output_root / secondary_name
            secondary_out.write_text(
                xyz_text(secondary_mol, f"WP4-B ETKDGv3+{secondary_method}; pre_energy={secondary_energy:.12f}"),
                encoding="utf-8",
            )
            formula = rdMolDescriptors.CalcMolFormula(primary_mol)
            smiles = Chem.MolToSmiles(Chem.RemoveHs(primary_mol), canonical=True, isomericSmiles=False)
            records.append({
                "N": n,
                "series": "4n" if n % 4 == 0 else "4n+2",
                "species": species,
                "formula": formula,
                "ring_sizes": ring_sizes(primary_mol),
                "canonical_smiles": smiles,
                "graph_sha256": hashlib.sha256(f"{smiles}|{formula}".encode()).hexdigest(),
                "primary": {
                    "path": primary_name,
                    "method": primary_method,
                    "sha256": sha256(primary_out),
                    "parent_or_source_sha256": source_sha,
                    "ez_sequence": ez_sequence(primary_mol),
                },
                "secondary": {
                    "path": secondary_name,
                    "method": f"ETKDGv3+{secondary_method}",
                    "attempted": args.attempts,
                    "embedded": len(secondary),
                    "lowest_prescreen_energy": secondary_energy,
                    "sha256": sha256(secondary_out),
                    "ez_sequence": ez_sequence(secondary_mol),
                },
            })
    manifest["record_count"] = len(records)
    manifest["elapsed_seconds"] = time.perf_counter() - started
    manifest_path = args.output_root / "input_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
