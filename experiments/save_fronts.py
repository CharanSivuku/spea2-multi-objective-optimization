"""Re-run seed 1 of every standard benchmark (team protocol) and save the final front.

The run is deterministic, so the saved front is the very front behind the
seed-1 row of ``raw_metrics_all.csv``; the hypervolume is re-computed and compared
with that row as a check.  Output: ``results/comparison/obtained_fronts/<name>.csv``.
"""
from __future__ import annotations

import csv
import sys
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_registry import build_registry  # noqa: E402
from run_benchmarks import protocol_settings, run_one  # noqa: E402

OUT = ROOT / "results" / "comparison" / "obtained_fronts"
RAW = ROOT / "results" / "data" / "standard_suite_team_protocol" / "per_benchmark"


def job(name):
    problem = build_registry()[name]
    s = protocol_settings(name)
    rows, fronts = run_one(
        problem, s["population"], s["archive"], s["generations"], runs=1,
        seed_start=1, final_set="nondominated", sbx_scheme="deb",
        mutation_eta=s["mutation_eta"],
    )
    return name, rows[0]["hv"], fronts[0]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = sorted(build_registry())
    with get_context("fork").Pool(9) as pool:
        for name, hv, front in pool.imap_unordered(job, names):
            with (OUT / f"{name}.csv").open("w", newline="") as f:
                csv.writer(f).writerows(front)
            with (RAW / name / "raw_metrics_all.csv").open() as f:
                ref = next(r for r in csv.DictReader(f) if r["seed"] == "1")
            ok = abs(float(ref["hv"]) - hv) < 1e-12
            print(f"{name:12s} points={len(front):4d} hv={hv:.10f} stored={float(ref['hv']):.10f} {'OK' if ok else 'MISMATCH'}", flush=True)
