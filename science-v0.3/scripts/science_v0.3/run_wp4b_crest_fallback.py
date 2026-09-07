from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    raw = args.project / "data/science_v0.3/raw/wp4b"
    input_dir = args.project / "data/science_v0.3/inputs/wp4b"
    audit_path = raw / "etkdg_discovery_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    targets = [row for row in audit["records"] if not row["final_four_no_new_unique_within_window"]]
    crest = shutil.which("crest")
    if crest is None:
        raise RuntimeError("CREST is unavailable in the active environment")
    version = subprocess.run([crest, "--version"], text=True, capture_output=True, check=False)
    results: list[dict[str, object]] = []
    for target in targets:
        n, species = int(target["N"]), str(target["species"])
        job_id = f"N{n:02d}_{species}_crest"
        output_xyz = input_dir / f"{job_id}.xyz"
        work = raw / "crest" / job_id
        work.mkdir(parents=True, exist_ok=True)
        source = input_dir / f"N{n:02d}_{species}_auditbest.xyz"
        local_input = work / "input.xyz"
        if not local_input.exists():
            shutil.copy2(source, local_input)
        log = work / "crest.log"
        command = [crest, "input.xyz", "--gfn2", "--quick", "-T", str(args.threads), "--chrg", "0", "--uhf", "0"]
        # CREST/xTB parallelizes its numerical work through OpenMP.  The
        # conda OpenBLAS pthread backend must stay single-threaded inside
        # those regions; otherwise it emits an unbounded warning stream and
        # may deadlock through nested parallelism.
        run_env = os.environ.copy()
        run_env.update({
            "OMP_NUM_THREADS": str(args.threads),
            "OMP_MAX_ACTIVE_LEVELS": "1",
            "OMP_NESTED": "FALSE",
            "OPENBLAS_NUM_THREADS": "1",
            "GOTO_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "BLIS_NUM_THREADS": "1",
        })
        started = time.perf_counter()
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                command,
                cwd=work,
                env=run_env,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
            )
        best = work / "crest_best.xyz"
        ensemble = work / "crest_conformers.xyz"
        valid = completed.returncode == 0 and best.exists()
        if valid:
            shutil.copy2(best, output_xyz)
        results.append({
            "id": job_id,
            "N": n,
            "species": species,
            "status": "COMPLETED" if valid else "FAILED",
            "returncode": completed.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "input_sha256": sha256(source),
            "best_xyz": str(output_xyz.relative_to(args.project)).replace("\\", "/") if valid else None,
            "best_sha256": sha256(output_xyz) if valid else None,
            "ensemble_present": ensemble.exists(),
            "ensemble_size_bytes": ensemble.stat().st_size if ensemble.exists() else 0,
            "log": str(log.relative_to(args.project)).replace("\\", "/"),
        })
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    summary = {
        "schema_version": "science-v0.3-wp4b-crest-fallback-1",
        "triggered_by": "ETKDG_32_ATTEMPT_STOP_RULE_FAILURE",
        "crest_version_output": (version.stdout + version.stderr).strip(),
        "threads": args.threads,
        "targets": [[int(row["N"]), str(row["species"])] for row in targets],
        "results": results,
        "all_triggered_targets_completed": bool(targets) and all(row["status"] == "COMPLETED" for row in results),
    }
    summary_path = raw / "crest_fallback_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not summary["all_triggered_targets_completed"]:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
