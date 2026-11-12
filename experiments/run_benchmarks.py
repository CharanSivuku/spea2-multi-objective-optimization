"""Run any of the 30 registered benchmarks (ZDT, DTLZ, classical) with SPEA2."""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import time
import sys

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))


from benchmark_registry import build_registry
from plot_front import plot_front

from src.spea2 import spea2

from src.metrics.mmo import nondominated_mask

from src.metrics.gd import calculate_gd
from src.metrics.igd import calculate_igd
from src.metrics.hypervolume import calculate_hypervolume
from src.metrics.spacing import calculate_spacing


def _reference_point(front):
    """Choose a minimization HV reference point beyond the reference front."""

    if not front:
        raise ValueError("Reference front cannot be empty")

    dimensions = len(front[0])

    reference = []

    for j in range(dimensions):
        values = [point[j] for point in front]

        maximum = max(values)
        minimum = min(values)

        margin = max(
            0.1,
            0.1 * (maximum - minimum)
        )

        reference.append(maximum + margin)

    return reference


def _finite_mean(values):
    """Mean ignoring NaN (runs with no feasible solution); NaN if none."""
    clean = [v for v in values if v == v]

    return statistics.mean(clean) if clean else float("nan")


def _calculate_nfe(
    population_size,
    archive_size,
    generations
):
    """Objective evaluations performed by the SPEA2 loop.

    Every solution is evaluated exactly once (the archive's objective values
    are cached), so the total is population_size * generations: the initial
    population plus one offspring batch per further iteration.
    ``generations = 1001`` therefore gives 100 + 1000 * 100 = 100,100
    evaluations. (Older result files used the formula
    ``P + (G - 1) * (P + A)``, which counted archive re-evaluations.)
    """
    return population_size * max(0, generations)


def protocol_settings(name, protocol="team"):
    """Population / archive / iterations / mutation index for one benchmark.

    ``team`` is the configuration shared with the NSGA-II comparison:

    * DTLZ1-7: population 200, 3,000 generations = 3001 iterations
      (200 + 3000 * 200 = 600,200 evaluations), polynomial-mutation index 10;
    * everything else: population 100, 1,000 generations = 1001 iterations
      (100 + 1000 * 100 = 100,100 evaluations), mutation index 20.

    ``uniform`` uses the second line for every benchmark.
    """
    if protocol == "team" and name.upper().startswith("DTLZ"):
        return {
            "population": 200, "archive": 200,
            "generations": 3001, "mutation_eta": 10,
        }

    return {
        "population": 100, "archive": 100,
        "generations": 1001, "mutation_eta": 20,
    }


def run_one(
    problem,
    population_size=100,
    archive_size=100,
    generations=1001,
    runs=5,
    seed_start=1,
    final_set="nondominated",
    sbx_scheme="deb",
    mutation_eta=20
):
    rows = []

    all_approximations = []

    hv_reference = _reference_point(
        problem.reference_front
    )

    nfe = _calculate_nfe(
        population_size,
        archive_size,
        generations
    )

    for seed in range(
        seed_start,
        seed_start + runs
    ):

        random.seed(seed)

        started = time.perf_counter()

        _, archive = spea2(
            population_size,
            problem.n_var,
            archive_size,
            generations,
            problem.lower,
            problem.upper,
            problem.objective,
            getattr(problem, "constraint", None),
            sbx_scheme,
            mutation_eta
        )

        elapsed = time.perf_counter() - started

        constraint = getattr(problem, "constraint", None)

        # Constrained problems: only feasible archive members are scored.
        feasible_archive = [
            solution
            for solution in archive
            if constraint is None or constraint(solution) <= 0.0
        ]

        approximation = [
            problem.objective(solution)
            for solution in feasible_archive
        ]

        if final_set == "nondominated" and approximation:
            # score only the non-dominated feasible solutions
            keep = nondominated_mask(approximation)
            approximation = [
                point for point, k in zip(approximation, keep) if k
            ]

        all_approximations.append(
            approximation
        )

        if approximation:
            hv = calculate_hypervolume(
                approximation,
                hv_reference
            )

            igd = calculate_igd(
                approximation,
                problem.reference_front
            )

            gd = calculate_gd(
                approximation,
                problem.reference_front
            )

            spacing = calculate_spacing(
                approximation
            )
        else:
            # No feasible solution found: metrics are undefined.
            hv = igd = gd = spacing = float("nan")

        rows.append({
            "benchmark": problem.name,
            "seed": seed,
            "hv": hv,
            "igd": igd,
            "gd": gd,
            "spacing": spacing,
            "archive_size": len(archive),
            "feasible_archive_size": len(feasible_archive),
            "scored_set_size": len(approximation),
            "nfe": nfe,
            "runtime_seconds": elapsed
        })

    return rows, all_approximations


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--benchmarks",
        nargs="+",
        help="Names, e.g. ZDT1 DTLZ2"
    )

    parser.add_argument(
        "--protocol",
        choices=["team", "uniform"],
        default="team",
        help="team (default): DTLZ pop 200 / 3001 iterations / mutation index 10, "
             "all others pop 100 / 1001 iterations / index 20; "
             "uniform: the latter for every benchmark. "
             "--population/--archive/--generations/--mutation-eta override it."
    )

    parser.add_argument(
        "--population",
        type=int,
        default=None
    )

    parser.add_argument(
        "--archive",
        type=int,
        default=None
    )

    parser.add_argument(
        "--generations",
        type=int,
        default=None,
        help="SPEA2 iterations (1001 = 100 + 1000 * 100 evaluations with population 100)."
    )

    parser.add_argument(
        "--mutation-eta",
        type=float,
        default=None,
        help="Polynomial-mutation distribution index."
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=5
    )

    parser.add_argument(
        "--dtlz-vars",
        type=int,
        default=12
    )

    parser.add_argument(
        "--objectives",
        type=int,
        default=3
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory for CSVs and figures. Defaults to "
            "'results/data/new_run'; existing files are never overwritten "
            "unless --overwrite is given."
        )
    )

    parser.add_argument(
        "--final-set",
        choices=["nondominated", "archive"],
        default="nondominated",
        help="Which solutions are scored: the non-dominated feasible ones "
             "(default) or the whole final archive (old behaviour)."
    )

    parser.add_argument(
        "--sbx-scheme",
        choices=["deb", "per_variable"],
        default="deb",
        help="SBX probability scheme: standard Deb (default) or the legacy "
             "per-variable scheme of the earlier experiments."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing result files."
    )

    parser.add_argument(
        "--seed-start",
        type=int,
        default=1,
        help="First random seed; runs use seed_start .. seed_start+runs-1."
    )

    args = parser.parse_args()

    if args.population is not None and args.population < 2:
        parser.error("--population must be at least 2")

    if args.archive is not None and args.archive < 1:
        parser.error("--archive must be at least 1")

    if args.generations is not None and args.generations < 1:
        parser.error("--generations must be at least 1")

    if args.runs < 1:
        parser.error("--runs must be at least 1")

    registry = build_registry(
        dtlz_n_var=args.dtlz_vars,
        n_obj=args.objectives
    )

    names = (
        args.benchmarks
        or list(registry)
    )

    unknown = sorted(
        set(names) - set(registry)
    )

    if unknown:
        parser.error(
            "Unknown benchmark(s): "
            + ", ".join(unknown)
        )

    root = ROOT

    results_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else root / "results" / "data" / "new_run"
    )

    figures_dir = results_dir / "figures"

    raw_file = results_dir / "raw_metrics_all.csv"
    summary_file = results_dir / "summary_metrics_all.csv"

    if not args.overwrite:
        protected = [raw_file, summary_file] + [
            figures_dir / f"{name.lower()}.png"
            for name in names
        ]

        existing = [str(p) for p in protected if p.exists()]

        if existing:
            parser.error(
                "Refusing to overwrite existing result files "
                "(use --output-dir for a new folder, or --overwrite):\n  "
                + "\n  ".join(existing)
            )

    figures_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    all_rows = []

    for name in names:

        problem = registry[name]

        settings = protocol_settings(name, args.protocol)

        rows, all_approximations = run_one(
            problem,
            population_size=args.population or settings["population"],
            archive_size=args.archive or settings["archive"],
            generations=args.generations or settings["generations"],
            runs=args.runs,
            seed_start=args.seed_start,
            final_set=args.final_set,
            sbx_scheme=args.sbx_scheme,
            mutation_eta=(
                args.mutation_eta
                if args.mutation_eta is not None
                else settings["mutation_eta"]
            )
        )

        all_rows.extend(rows)

        print(
            f"\n{name}: "
            + " | ".join(
                f"{metric.upper()} "
                f"{_finite_mean([r[metric] for r in rows]):.6g}"
                for metric in (
                    "hv",
                    "igd",
                    "gd",
                    "spacing"
                )
            )
        )

        print(
            f"Runs: {args.runs} | "
            f"Seeds: {args.seed_start}-"
            f"{args.seed_start + args.runs - 1} | "
            f"NFE per run: {rows[0]['nfe']}"
        )

        # Combine approximation points from all independent runs.
        combined_approximation = [
            point
            for run_front in all_approximations
            for point in run_front
        ]

        figure_path = (
            figures_dir
            / f"{name.lower()}.png"
        )

        if combined_approximation:
            plot_front(
                combined_approximation,
                problem.reference_front,
                f"{name} - SPEA2 ({args.runs} runs)",
                str(figure_path)
            )

            print(f"Plot saved: {figure_path}")
        else:
            print(f"No feasible solutions found for {name}; no plot.")

    # Save individual-run metrics.
    fields = [
        "benchmark",
        "seed",
        "hv",
        "igd",
        "gd",
        "spacing",
        "archive_size",
        "feasible_archive_size",
        "scored_set_size",
        "nfe",
        "runtime_seconds"
    ]

    with raw_file.open(
        "w",
        newline=""
    ) as stream:

        writer = csv.DictWriter(
            stream,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(all_rows)

    # Save mean and standard deviation for each benchmark.
    with summary_file.open(
        "w",
        newline=""
    ) as stream:

        fields_summary = (
            ["benchmark", "runs"]
            + [
                f"{metric}_{stat}"
                for metric in (
                    "hv",
                    "igd",
                    "gd",
                    "spacing"
                )
                for stat in (
                    "mean",
                    "std"
                )
            ]
        )

        writer = csv.DictWriter(
            stream,
            fieldnames=fields_summary
        )

        writer.writeheader()

        for name in names:

            selected = [
                row
                for row in all_rows
                if row["benchmark"] == name
            ]

            summary_row = {
                "benchmark": name,
                "runs": len(selected)
            }

            for metric in (
                "hv",
                "igd",
                "gd",
                "spacing"
            ):

                values = [
                    row[metric]
                    for row in selected
                    if row[metric] == row[metric]  # drop NaN
                ]

                summary_row[
                    f"{metric}_mean"
                ] = _finite_mean(values)

                summary_row[
                    f"{metric}_std"
                ] = (
                    statistics.stdev(values)
                    if len(values) > 1
                    else 0.0
                )

            writer.writerow(summary_row)

    print("\nExperiment completed.")

    print(f"Raw metrics saved: {raw_file}")
    print(f"Summary metrics saved: {summary_file}")


if __name__ == "__main__":
    main()
