"""Run SPEA2 on the 24 CEC 2020 multimodal multi-objective (MMO) problems.

Two protocols (``--protocol``):

* ``team`` (default): the protocol shared with the NSGA-II comparison:
  population = archive = 100, 201 iterations (100 + 200 * 100 = 20,100
  evaluations), 3 runs with seeds 1-3.
* ``official``: the technical report (section 2.2) and the organisers'
  example harness `main.m`: 21 runs, population 200 * N_ops, maximum
  evaluations 10000 * N_ops, i.e. ``MaxFES / popsize = 50`` iterations.

In both, every new solution is evaluated once, the obtained sets are the
non-dominated members of the final archive, and the indicators (all
smaller-is-better) are 1/PSP, 1/HV, IGDX and IGDF.

SPEA2 is the project's real-coded SPEA2 (SBX / polynomial mutation, archive size
equal to the population size), *not* the organisers' MATLAB SPEA2, and has no
niching in decision space, so it is expected to cover few of the multiple
Pareto sets. It is reported as-is.

Outputs (in --output-dir, never overwriting existing files unless --overwrite):
  raw_metrics_all.csv       one row per run (indicators, CR, PSP, HV, seed, ...)
  summary_metrics_all.csv   best / worst / mean / median / std per indicator
  figures/<name>.png        obtained vs reference PS and PF of the median-1/PSP run
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from plot_mmo import plot_mmo  # noqa: E402
from src.benchmarks.cec2020_mmo import MMO_NAMES, get_problem  # noqa: E402
from src.metrics import calculate_gd, calculate_spacing  # noqa: E402
from src.metrics.mmo import mmo_indicators, nondominated_mask  # noqa: E402
from src.spea2 import spea2  # noqa: E402

INDICATORS = ("rPSP", "rHV", "IGDX", "IGDF")
# objective-space indicators in the layout of the standard suite (HV is the plain
# hypervolume, IGD is IGDF), so that MMO results can be compared like the others
EXTRA = ("HV", "GD", "spacing")


def run_once(job):
    """One independent run of one problem (picklable job tuple)."""
    name, seed, generations = job[:3]

    problem = get_problem(name)
    reference_ps = problem.reference_ps()
    reference_pf = problem.reference_pf()
    pop = job[3] if len(job) > 3 and job[3] else problem.population_size

    random.seed(seed)
    started = time.perf_counter()

    _, archive = spea2(
        pop, problem.n_var, pop, generations,
        problem.lower, problem.upper, problem.objective,
    )

    runtime = time.perf_counter() - started

    objectives = np.array([problem.objective(x) for x in archive])
    solutions = np.array(archive)
    keep = nondominated_mask(objectives)
    ps, pf = solutions[keep], objectives[keep]

    indicators = mmo_indicators(
        ps, pf, reference_ps, reference_pf,
        problem.hv_reference_point, name,
    )

    front = [[float(v) for v in row] for row in pf]
    indicators["GD"] = calculate_gd(front, reference_pf.tolist())
    indicators["spacing"] = calculate_spacing(front)

    return {
        "problem": name,
        "seed": seed,
        **indicators,
        "archive_size": len(archive),
        "n_nondominated": int(keep.sum()),
        "evaluations": pop * generations,
        "runtime_seconds": runtime,
        "ps": ps,
        "pf": pf,
    }


def _stats(values):
    finite = [v for v in values if v == v]

    return {
        "best": min(finite),
        "worst": max(finite),
        "mean": statistics.mean(finite),
        "median": statistics.median(finite),
        "std": statistics.stdev(finite) if len(finite) > 1 else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--problems", nargs="+", default=list(MMO_NAMES))
    parser.add_argument(
        "--protocol", choices=["team", "official"], default="team",
        help="team: pop 100, 201 iterations, 3 runs (default); "
             "official: CEC 2020 report (pop 200*N_ops, 50 iterations, 21 runs)."
    )
    parser.add_argument("--runs", type=int, default=None,
                        help="Default: 3 (team) or 21 (official).")
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument(
        "--generations", type=int, default=None,
        help="Override the iteration count (team: 201, official: MaxFES / popsize = 50)."
    )
    parser.add_argument(
        "--population", type=int, default=None,
        help="Override the population/archive size (team: 100, official: 200*N_ops)."
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    team = args.protocol == "team"
    runs = args.runs or (3 if team else 21)
    population = args.population or (100 if team else None)

    unknown = sorted(set(args.problems) - set(MMO_NAMES))

    if unknown:
        parser.error("Unknown problem(s): " + ", ".join(unknown))

    out = (
        Path(args.output_dir).resolve() if args.output_dir
        else ROOT / "results" / "data" / "new_run_cec2020_mmo"
    )
    raw_file = out / "raw_metrics_all.csv"
    summary_file = out / "summary_metrics_all.csv"
    figures = out / "figures"

    if not args.overwrite:
        protected = [raw_file, summary_file] + [
            figures / f"{n.lower()}.png" for n in args.problems
        ]
        existing = [str(p) for p in protected if p.exists()]

        if existing:
            parser.error(
                "Refusing to overwrite existing files (use --output-dir or "
                "--overwrite):\n  " + "\n  ".join(existing)
            )

    figures.mkdir(parents=True, exist_ok=True)

    jobs = []

    for name in args.problems:
        generations = args.generations or (
            201 if team else get_problem(name).generations
        )

        for run in range(runs):
            jobs.append((name, args.seed_start + run, generations, population))

    if args.workers > 1:
        with get_context("fork").Pool(args.workers) as pool:
            results = pool.map(run_once, jobs, chunksize=1)
    else:
        results = [run_once(job) for job in jobs]

    raw_fields = [
        "problem", "run", "seed", *INDICATORS, "CR", "PSP", "HV", "GD", "spacing",
        "archive_size", "n_nondominated", "evaluations", "runtime_seconds",
    ]
    raw_rows, summary_rows = [], []

    for name in args.problems:
        problem = get_problem(name)
        runs = [r for r in results if r["problem"] == name]

        for index, r in enumerate(runs, start=1):
            raw_rows.append({"run": index, **{k: r[k] for k in raw_fields if k != "run"}})

        summary = {"problem": name, "runs": len(runs), "n_ops": problem.n_ops}

        for indicator in (*INDICATORS, *EXTRA):
            for stat, value in _stats([r[indicator] for r in runs]).items():
                summary[f"{indicator}_{stat}"] = value

        summary_rows.append(summary)

        # figure of the run with the median 1/PSP (as the organisers suggest)
        order = sorted(range(len(runs)), key=lambda i: runs[i]["rPSP"])
        median_run = runs[order[len(order) // 2]]
        plot_mmo(
            name, median_run["ps"], median_run["pf"],
            problem.reference_ps(), problem.reference_pf(),
            figures / f"{name.lower()}.png",
            f"({len(runs)} runs, median-1/PSP run shown)",
        )

        print(
            f"{name:10s} 1/PSP {summary['rPSP_mean']:.4g}  1/HV {summary['rHV_mean']:.4g}  "
            f"IGDX {summary['IGDX_mean']:.4g}  IGDF {summary['IGDF_mean']:.4g}"
        )

    for path, rows, fields in (
        (raw_file, raw_rows, raw_fields),
        (summary_file, summary_rows, list(summary_rows[0])),
    ):
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"\nRaw: {raw_file}\nSummary: {summary_file}\nFigures: {figures}")


if __name__ == "__main__":
    main()
