from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--threads-per-job", type=int, default=4)
    args = parser.parse_args()
    raw = args.project / "data/science_v0.3/raw/wp4b"
    inputs = args.project / "data/science_v0.3/inputs/wp4b"
    runner = args.project / "scripts/science_v0.3/run_wp4b_bs_check.py"

    def run_one(n: int, species: str) -> dict[str, object]:
        job_id = f"N{n:02d}_{species}_source_bs"
        output = raw / f"{job_id}.json"
        log = raw / f"{job_id}.log"
        cmd = [
            sys.executable, str(runner),
            "--input", str(inputs / f"N{n:02d}_{species}_source.xyz"),
            "--output", str(output), "--N", str(n), "--species", species,
            "--threads", str(args.threads_per_job),
        ]
        started = time.perf_counter()
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, check=False)
        return {
            "id": job_id,
            "status": "COMPLETED" if completed.returncode == 0 and output.exists() else "FAILED",
            "returncode": completed.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "output": str(output), "log": str(log),
        }

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, n, species) for n in (16, 32) for species in ("A", "C")]
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    summary = {
        "schema_version": "science-v0.3-wp4b-bs-batch-1",
        "workers": args.workers,
        "threads_per_job": args.threads_per_job,
        "results": sorted(results, key=lambda row: str(row["id"])),
    }
    (raw / "source_geometry_bs_batch.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if any(row["status"] == "FAILED" for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
