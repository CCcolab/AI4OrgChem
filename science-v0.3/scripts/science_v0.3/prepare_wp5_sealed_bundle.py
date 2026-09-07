from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


RUNNER = r'''from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

from pyscf import dft, gto, lib


ROOT = Path(__file__).resolve().parent
task = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
lib.num_threads(int(task["threads"]))
mol = gto.M(
    atom=[(row[0], tuple(row[1:])) for row in task["atoms_angstrom"]],
    unit="Angstrom",
    basis=task["basis"],
    charge=0,
    spin=0,
    symmetry=False,
    cart=False,
    verbose=4,
    output=str(ROOT / "calculation.log"),
)
mf = dft.RKS(mol)
mf.xc = task["xc"]
mf.conv_tol = task["scf_energy_tolerance_hartree"]
mf.max_cycle = task["max_scf_cycles"]
mf.direct_scf = True
mf.grids.atom_grid = {symbol: tuple(grid) for symbol, grid in task["atom_grid"].items()}
mf.grids.prune = dft.gen_grid.nwchem_prune
energy = float(mf.kernel())
log = ROOT / "calculation.log"
result = {
    "schema_version": "science-v0.3-wp5-sealed-result-1",
    "anchor_id": task["anchor_id"],
    "program": "PySCF",
    "program_version": __import__("pyscf").__version__,
    "python_version": platform.python_version(),
    "converged": bool(mf.converged),
    "energy_hartree": energy,
    "retained_grid_points": int(mf.grids.coords.shape[0]),
    "task_sha256": hashlib.sha256((ROOT / "task.json").read_bytes()).hexdigest(),
    "raw_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
}
(ROOT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"converged": result["converged"], "result": "result.json"}))
raise SystemExit(0 if result["converged"] else 2)
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    contract_path = project / "configs/science_v0.3/wp5_external_replay_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    source_path = project / contract["target"]["geometry_source"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    atoms = source["optimized_G_geometry"]["atoms_angstrom"]
    replay_root = project / "runs/science_v0.3/wp5_external_replay"
    sealed = replay_root / "sealed_input"
    sealed.mkdir(parents=True, exist_ok=True)
    task = {
        "schema_version": "science-v0.3-wp5-sealed-task-1",
        "anchor_id": contract["target"]["anchor_id"],
        "relation_type": "SAME_ESTIMAND",
        "atoms_angstrom": atoms,
        "charge": 0,
        "multiplicity": 1,
        "xc": "B3LYPG",
        "basis": "6-31g*",
        "spherical_basis": True,
        "density_fitting": False,
        "dispersion": "none",
        "scf_energy_tolerance_hartree": 1e-10,
        "max_scf_cycles": 200,
        "atom_grid": {"H": [300, 1202], "C": [300, 1454]},
        "pruning": "nwchem_prune",
        "threads": 4,
        "reference_energy_in_bundle": False
    }
    (sealed / "task.json").write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
    (sealed / "runner.py").write_text(RUNNER, encoding="utf-8")
    prompt = (
        "You are an independent replay agent. Inspect the sealed task manifest without "
        "guessing a target value. Return exactly one JSON object with action "
        "RUN_REGISTERED_REPLAY, runner runner.py, output result.json, and a short "
        "protocol_check string. Do not emit shell commands or modify scientific settings."
    )
    (sealed / "agent_task.txt").write_text(prompt + "\n", encoding="utf-8")
    files = []
    for path in sorted(sealed.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            files.append({"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "schema_version": "science-v0.3-wp5-sealed-manifest-1",
        "contract_sha256": sha256(contract_path),
        "source_geometry_sha256": sha256(source_path),
        "reference_energy_present": False,
        "files": files,
    }
    (sealed / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sealed_bundle": str(sealed), "files": len(files), "reference_energy_present": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
