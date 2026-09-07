from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_id(path: Path) -> tuple[int, str, str, str]:
    stem = path.stem
    n_text, species, source = stem.split("_")
    return int(n_text[1:]), species, source, stem


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--threads-per-job", type=int, default=4)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument(
        "--n-values",
        default="8,10",
        help="Comma-separated subset of the frozen paired pilot: 8,10,16,18,32,34.",
    )
    parser.add_argument(
        "--sources",
        default="source,etkdg",
        help="Comma-separated conformer sources: source,etkdg,auditbest,crest.",
    )
    parser.add_argument(
        "--summary-name",
        default="small_conformer_screen_batch.json",
    )
    args = parser.parse_args()
    n_values = {int(value) for value in args.n_values.split(",") if value.strip()}
    sources = {value.strip() for value in args.sources.split(",") if value.strip()}
    if not n_values <= {8, 10, 16, 18, 32, 34}:
        raise ValueError("--n-values contains an N outside the frozen paired pilot")
    if not sources <= {"source", "etkdg", "auditbest", "crest"}:
        raise ValueError("--sources must be a subset of source,etkdg,auditbest,crest")

    input_dir = args.project / "data/science_v0.3/inputs/wp4b"
    output_dir = args.project / "data/science_v0.3/raw/wp4b"
    runner = args.project / "scripts/science_v0.3/run_wp4b_small_dft.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(
        p
        for p in input_dir.glob("N*_*.xyz")
        if int(p.stem.split("_")[0][1:]) in n_values
        and p.stem.rsplit("_", 1)[-1] in sources
        and p.stem not in set(args.exclude)
    )

    def run_one(path: Path) -> dict[str, object]:
        n, species, source, job_id = parse_id(path)
        output = output_dir / f"{job_id}.json"
        log = output_dir / f"{job_id}.log"
        if output.exists():
            return {"id": job_id, "status": "SKIPPED_EXISTING", "returncode": 0}
        cmd = [
            sys.executable,
            str(runner),
            "--input", str(path),
            "--output", str(output),
            "--N", str(n),
            "--species", species,
            "--source", source,
            "--threads", str(args.threads_per_job),
            "--energy-only",
        ]
        started = time.perf_counter()
        environment = os.environ.copy()
        environment.update({
            "OMP_NUM_THREADS": str(args.threads_per_job),
            "OPENBLAS_NUM_THREADS": str(args.threads_per_job),
            "MKL_NUM_THREADS": str(args.threads_per_job),
        })
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                cmd,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
                env=environment,
            )
        return {
            "id": job_id,
            "status": "COMPLETED" if completed.returncode == 0 and output.exists() else "FAILED",
            "returncode": completed.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "output": str(output),
            "log": str(log),
        }

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, path): path for path in inputs}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)

    summary = {
        "schema_version": "science-v0.3-wp4b-small-batch-1",
        "workers": args.workers,
        "threads_per_job": args.threads_per_job,
        "excluded": args.exclude,
        "n_values": sorted(n_values),
        "sources": sorted(sources),
        "results": sorted(results, key=lambda row: str(row["id"])),
    }
    summary_path = output_dir / args.summary_name
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if any(row["status"] == "FAILED" for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
