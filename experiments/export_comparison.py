"""Export SPEA2 results in a layout that other algorithms can be compared against.

Writes results/comparison/ (derived from the final result files, nothing is rerun):

  spea2_runs.csv           one row per run: problem, algorithm, seed, HV, IGD, GD,
                           spacing, runtime_seconds, evaluations
  spea2_summary.csv        mean and standard deviation per problem
  spea2_mmo_runs.csv       CEC 2020 MMO: problem, algorithm, seed, rPSP, rHV, IGDX, IGDF, HV, IGD, GD, spacing, ...
  spea2_mmo_summary.csv
  hv_reference_points.csv  the hypervolume reference point used for every problem
  reference_fronts/<problem>.csv   the reference front used for IGD / GD / HV
  README.md                definitions needed to reproduce / compare the numbers
"""

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_registry import build_registry  # noqa: E402
from run_benchmarks import _reference_point  # noqa: E402

RESULTS = ROOT / "results"
OUT = RESULTS / "comparison"
ALGORITHM = "SPEA2"


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_rows(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarise(rows, key, metrics):
    out = []

    for problem in dict.fromkeys(r[key] for r in rows):
        sel = [r for r in rows if r[key] == problem]
        row = {"problem": problem, "algorithm": ALGORITHM, "runs": len(sel)}

        for m in metrics:
            values = [float(r[m]) for r in sel]
            row[f"{m}_mean"] = statistics.mean(values)
            row[f"{m}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0

        out.append(row)

    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reference_fronts").mkdir(exist_ok=True)

    # ---- standard suite
    raw = read_rows(RESULTS / "data/standard_suite_team_protocol/raw_metrics_all.csv")
    runs = [{
        "problem": r["benchmark"], "algorithm": ALGORITHM, "seed": r["seed"],
        "HV": r["hv"], "IGD": r["igd"], "GD": r["gd"], "spacing": r["spacing"],
        "runtime_seconds": r["runtime_seconds"], "evaluations": r["nfe"],
    } for r in raw]
    write_rows(OUT / "spea2_runs.csv", runs, list(runs[0]))

    summary = summarise(runs, "problem", ["HV", "IGD", "GD", "spacing"])
    write_rows(OUT / "spea2_summary.csv", summary, list(summary[0]))

    # ---- reference fronts and HV reference points
    registry = build_registry()
    hv_rows = []

    for name, problem in registry.items():
        front = problem.reference_front
        write_rows(
            OUT / "reference_fronts" / f"{name}.csv",
            [{f"f{i + 1}": v for i, v in enumerate(p)} for p in front],
            [f"f{i + 1}" for i in range(problem.n_obj)],
        )
        point = _reference_point(front)
        hv_rows.append({
            "problem": name, "n_obj": problem.n_obj,
            "reference_front_points": len(front),
            **{f"ref_f{i + 1}": v for i, v in enumerate(point)},
        })

    write_rows(OUT / "hv_reference_points.csv", hv_rows,
               ["problem", "n_obj", "reference_front_points", "ref_f1", "ref_f2", "ref_f3"])

    # ---- CEC 2020 MMO
    mmo = read_rows(RESULTS / "data/cec2020_mmo_team_protocol/raw_metrics_all.csv")
    mmo_runs = [{
        "problem": r["problem"], "algorithm": ALGORITHM, "seed": r["seed"],
        "rPSP": r["rPSP"], "rHV": r["rHV"], "IGDX": r["IGDX"], "IGDF": r["IGDF"],
        "HV": r["HV"], "IGD": r["IGDF"], "GD": r["GD"], "spacing": r["spacing"],
        "runtime_seconds": r["runtime_seconds"], "evaluations": r["evaluations"],
    } for r in mmo]
    write_rows(OUT / "spea2_mmo_runs.csv", mmo_runs, list(mmo_runs[0]))
    mmo_summary = summarise(mmo_runs, "problem", ["rPSP", "rHV", "IGDX", "IGDF", "HV", "IGD", "GD", "spacing"])
    write_rows(OUT / "spea2_mmo_summary.csv", mmo_summary, list(mmo_summary[0]))

    print("exported:", len(runs), "standard runs,", len(registry), "reference fronts,", len(mmo_runs), "MMO runs")


if __name__ == "__main__":
    main()
