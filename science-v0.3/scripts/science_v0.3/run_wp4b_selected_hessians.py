from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--threads-per-job", type=int, default=4)
    parser.add_argument("--selection-name", default="paired_conformer_selection.json")
    parser.add_argument("--summary-name", default="paired_selected_hessian_batch.json")
    args = parser.parse_args()
    raw = args.project / "data/science_v0.3/raw/wp4b"
    selection = json.loads((raw / args.selection_name).read_text(encoding="utf-8"))
    if not selection.get("complete"):
        raise RuntimeError("Conformer selection is incomplete")
    runner = args.project / "scripts/science_v0.3/run_wp4b_small_dft.py"
    input_dir = args.project / "data/science_v0.3/inputs/wp4b"

    def run_one(row: dict[str, object]) -> dict[str, object]:
        job_id = str(row["id"])
        n = int(row["N"])
        species = str(row["species"])
        source = job_id.rsplit("_", 1)[-1]
        output = raw / f"{job_id}.json"
        log = raw / f"{job_id}.frequency.log"
        if n >= 16 and source == "source" and not output.exists():
            return {
                "id": job_id,
                "status": "SKIPPED_PUBLISHED_SOURCE_MINIMUM",
                "returncode": 0,
                "elapsed_seconds": 0.0,
                "output": "configs/science_v0.3/wp4b_source_0k_anchors.json",
                "log": None,
            }
        if output.exists():
            existing = json.loads(output.read_text(encoding="utf-8"))
            if "e0_hartree" in existing and existing.get("minimum") is True:
                return {
                    "id": job_id,
                    "status": "SKIPPED_VALID_EXISTING",
                    "returncode": 0,
                    "elapsed_seconds": 0.0,
                    "output": str(output),
                    "log": str(log),
                }
        cmd = [
            sys.executable, str(runner),
            "--input", str(input_dir / f"{job_id}.xyz"),
            "--output", str(output),
            "--N", str(n), "--species", species, "--source", source,
            "--threads", str(args.threads_per_job),
        ]
        started = time.perf_counter()
        environment = os.environ.copy()
        environment.update({
            "OMP_NUM_THREADS": str(args.threads_per_job),
            "OPENBLAS_NUM_THREADS": str(args.threads_per_job),
            "MKL_NUM_THREADS": str(args.threads_per_job),
            "OMP_MAX_ACTIVE_LEVELS": "1",
        })
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                cmd,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
                env=environment,
            )
        valid = False
        if completed.returncode == 0 and output.exists():
            data = json.loads(output.read_text(encoding="utf-8"))
            valid = data.get("schema_version") in {
                "science-v0.3-wp4b-small-dft-result-1",
                "science-v0.3-wp4b-dft-result-2",
            }
        return {
            "id": job_id,
            "status": "COMPLETED" if valid else "FAILED",
            "returncode": completed.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "output": str(output),
            "log": str(log),
        }

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, row) for row in selection["selected"]]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    summary = {
        "schema_version": "science-v0.3-wp4b-selected-hessian-batch-1",
        "workers": args.workers,
        "threads_per_job": args.threads_per_job,
        "results": sorted(results, key=lambda row: str(row["id"])),
    }
    (raw / args.summary_name).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if any(row["status"] == "FAILED" for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
