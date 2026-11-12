"""Run SPEA2 on the CEC 2022 single-objective suite (12 functions, D = 10, 20).

Follows the technical report's protocol:

* 30 runs per function and dimension, seeds from the official ``Rand_Seeds.txt``
  (``seed_ind`` rule), bounds [-100, 100]^D;
* MaxFES = 200,000 (D = 10) and 1,000,000 (D = 20); every solution evaluation
  counts once (SPEA2 caches the archive's objective values);
* stop when the error F(x) - F* drops below 1e-8;
* record the best error at the 16 checkpoints
  floor(D^(k/5-3) * MaxFES), k = 0..15, plus FEterm (evaluations at termination).

SPEA2 is a multi-objective algorithm: here it runs with a single objective, where
Pareto dominance reduces to ranking by function value. It is *not* tuned for
these problems and is reported as-is; population/archive sizes are 100/100
unless overridden, with the project's original per-variable SBX scheme (see
DEFAULT_SBX_SCHEME).

Outputs (in --output-dir, never overwriting existing files unless --overwrite;
results are written after every (function, dimension) group, and an
interrupted run can be continued with --resume):
  raw_metrics_all.csv      one row per run
  summary_metrics_all.csv  best / worst / median / mean / std of the final error
  results_format/SPEA2_<f>_<D>.txt  17 x 30 matrices in the competition format
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
import time
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.benchmarks.cec2022 import (  # noqa: E402
    CEC2022Function, F_STAR, SUPPORTED_DIMENSIONS, run_seed,
)
from src.spea2 import spea2  # noqa: E402

TARGET_ERROR = 1e-8
MAX_FES = {10: 200_000, 20: 1_000_000}

# The CEC 2022 experiments keep their original SPEA2 settings (population 100,
# archive 100, SBX applied to every variable with probability 0.9, mutation
# 1/n with index 20). They are *not* aligned with the NSGA-II comparison
# protocol used for the multi-objective suites, which uses the Deb SBX scheme.
DEFAULT_SBX_SCHEME = "per_variable"


class _Finished(Exception):
    """Raised from inside the objective to stop SPEA2 at the budget/target."""


class FESTracker:
    """Counts evaluations, tracks the best error and records the checkpoints."""

    def __init__(self, function: CEC2022Function, max_fes: int):
        self.function = function
        self.max_fes = max_fes
        dim = function.dim

        self.checkpoints = [
            math.floor(dim ** (k / 5 - 3) * max_fes) for k in range(16)
        ]
        self.checkpoints[-1] = max_fes

        self.fes = 0
        self.best_error = float("inf")
        self.records = [None] * 16
        self._next = 0
        self.fe_term = None

    def __call__(self, x):
        error = self.function.error(x)
        self.fes += 1

        if error < self.best_error:
            self.best_error = error

        reached = self.best_error < TARGET_ERROR

        while self._next < 16 and (
            self.fes >= self.checkpoints[self._next] or reached
        ):
            self.records[self._next] = (
                TARGET_ERROR if reached else self.best_error
            )
            self._next += 1

        if reached or self.fes >= self.max_fes:
            self.fe_term = self.fes
            raise _Finished

        return [self.function.f_star + error]

    def column(self):
        """17-entry result column (16 checkpoint errors + FEterm)."""
        return [
            TARGET_ERROR if (v is not None and v < TARGET_ERROR) else v
            for v in self.records
        ] + [self.fe_term]


def run_once(job):
    """One independent run. Returns a dict (picklable)."""
    func_num, dim, run_id, runs, population, archive, max_fes = job[:7]
    sbx_scheme = job[7] if len(job) > 7 else DEFAULT_SBX_SCHEME

    function = CEC2022Function(func_num, dim)
    seed = run_seed(dim, func_num, run_id, runs)
    random.seed(seed)

    tracker = FESTracker(function, max_fes)
    started = time.perf_counter()

    try:
        # generations is an upper bound; the tracker stops the run at MaxFES
        spea2(
            population, dim, archive,
            max_fes // population + 2,
            function.lower, function.upper,
            tracker,
            sbx_scheme=sbx_scheme,
        )
    except _Finished:
        pass

    return {
        "function": func_num,
        "dim": dim,
        "run": run_id,
        "seed": seed,
        "final_error": tracker.best_error,
        "fe_term": tracker.fe_term,
        "runtime_seconds": time.perf_counter() - started,
        "column": tracker.column(),
    }


def _stats(values):
    return {
        "best": min(values),
        "worst": max(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--functions", nargs="+", type=int, default=list(F_STAR))
    parser.add_argument("--dims", nargs="+", type=int, default=list(SUPPORTED_DIMENSIONS))
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--population", type=int, default=100)
    parser.add_argument("--archive", type=int, default=100)
    parser.add_argument(
        "--max-fes-scale", type=float, default=1.0,
        help="Scale MaxFES (1.0 = official budget; <1 only for quick tests)."
    )
    parser.add_argument(
        "--sbx-scheme", choices=["per_variable", "deb"],
        default=DEFAULT_SBX_SCHEME,
        help="SBX probability scheme; the default reproduces the original "
             "CEC 2022 settings of this project."
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--resume", action="store_true",
        help="Continue an interrupted run: skip finished (function, dim) groups."
    )
    args = parser.parse_args()

    for f in args.functions:
        if f not in F_STAR:
            parser.error(f"Unknown function {f} (1..12)")

    for d in args.dims:
        if d not in SUPPORTED_DIMENSIONS:
            parser.error(f"Unsupported dimension {d} (10 or 20)")

    out = (
        Path(args.output_dir).resolve() if args.output_dir
        else ROOT / "results" / "data" / "new_run_cec2022"
    )
    raw_file = out / "raw_metrics_all.csv"
    summary_file = out / "summary_metrics_all.csv"
    results_dir = out / "results_format"

    if not args.overwrite and not args.resume:
        existing = [str(p) for p in (raw_file, summary_file) if p.exists()]

        if existing:
            parser.error(
                "Refusing to overwrite existing files (use --output-dir, "
                "--resume to continue an interrupted run, or --overwrite):\n  "
                + "\n  ".join(existing)
            )

    results_dir.mkdir(parents=True, exist_ok=True)

    raw_fields = [
        "function", "dim", "run", "seed", "final_error", "fe_term",
        "runtime_seconds",
    ]
    summary_fields = ["function", "dim", "runs", "best", "worst", "median", "mean", "std"]

    def group_done(func, dim):
        return (results_dir / f"SPEA2_{func}_{dim}.txt").exists()

    def keep_finished_rows(path, fields):
        """On resume: drop rows of groups whose result file was not completed."""
        rows = []

        if path.exists():
            with path.open(newline="") as stream:
                rows = [
                    r for r in csv.DictReader(stream)
                    if group_done(int(r["function"]), int(r["dim"]))
                ]

        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    if args.resume:
        keep_finished_rows(raw_file, raw_fields)
        keep_finished_rows(summary_file, summary_fields)
    else:
        for path, fields in ((raw_file, raw_fields), (summary_file, summary_fields)):
            with path.open("w", newline="") as stream:
                csv.DictWriter(stream, fieldnames=fields).writeheader()

    pool = get_context("fork").Pool(args.workers) if args.workers > 1 else None

    try:
        for dim in args.dims:
            max_fes = max(1, int(MAX_FES[dim] * args.max_fes_scale))

            for func in args.functions:
                if args.resume and group_done(func, dim):
                    print(f"F{func:<2d} D{dim}: already done, skipped", flush=True)
                    continue

                jobs = [
                    (func, dim, run_id, args.runs, args.population,
                     args.archive, max_fes, args.sbx_scheme)
                    for run_id in range(1, args.runs + 1)
                ]

                if pool:
                    results = pool.map(run_once, jobs, chunksize=1)
                else:
                    results = [run_once(job) for job in jobs]

                runs = sorted(results, key=lambda r: r["run"])
                stats = _stats([max(r["final_error"], TARGET_ERROR) for r in runs])

                # rows first, the completion marker (results file) last
                with raw_file.open("a", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=raw_fields)
                    writer.writerows({k: r[k] for k in raw_fields} for r in runs)

                with summary_file.open("a", newline="") as stream:
                    csv.DictWriter(stream, fieldnames=summary_fields).writerow(
                        {"function": func, "dim": dim, "runs": len(runs), **stats}
                    )

                with (results_dir / f"SPEA2_{func}_{dim}.txt").open("w") as fh:
                    for row in range(17):
                        fh.write(
                            "\t".join(f"{r['column'][row]:.8e}" if row < 16
                                      else str(r["column"][row]) for r in runs)
                            + "\n"
                        )

                print(
                    f"F{func:<2d} D{dim}: best {stats['best']:.4e}  mean "
                    f"{stats['mean']:.4e}  std {stats['std']:.3e}",
                    flush=True,
                )
    finally:
        if pool:
            pool.close()
            pool.join()

    print(f"\nRaw: {raw_file}\nSummary: {summary_file}")


if __name__ == "__main__":
    main()
