"""Combine the per-benchmark results of the standard suite.

Reads (never modifies) results/data/standard_suite_team_protocol/per_benchmark/<Name>/
and writes:

  results/data/standard_suite_team_protocol/raw_metrics_all.csv
  results/data/standard_suite_team_protocol/summary_metrics_all.csv
  results/figures/<name>.png                  (copied, one per benchmark)
  results/all_benchmarks_summary.csv          one row per benchmark (30)
"""

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SET = RESULTS / "data" / "standard_suite_team_protocol"

ALL_30 = (
    ["ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6"]
    + [f"DTLZ{i}" for i in range(1, 8)]
    + ["Binh1", "Binh3", "Deb", "Deb2", "Fonseca", "Fonseca2", "Kursawe",
       "Laumanns", "Murata", "Quagliarella", "Rendon", "Rendon2",
       "Schaffer", "Schaffer2", "Srinivas", "Tanaka", "Viennet", "Viennet2"]
)

NOTES = {
    "Binh3": "single-point front; HV is only the reference-point margin",
    "Quagliarella": "front extremes need all 16 variables at 0 or 1.5",
}


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    raw_rows, summary_rows = [], []
    (RESULTS / "figures").mkdir(parents=True, exist_ok=True)

    for name in ALL_30:
        folder = SET / "per_benchmark" / name
        raw_rows += read_rows(folder / "raw_metrics_all.csv")
        summary_rows += read_rows(folder / "summary_metrics_all.csv")
        shutil.copy(
            folder / "figures" / f"{name.lower()}.png",
            RESULTS / "figures" / f"{name.lower()}.png",
        )

    for filename, rows in (
        ("raw_metrics_all.csv", raw_rows),
        ("summary_metrics_all.csv", summary_rows),
    ):
        with (SET / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    evaluations = {r["benchmark"]: int(float(r["nfe"])) for r in raw_rows}
    population = {r["benchmark"]: int(float(r["archive_size"])) for r in raw_rows}

    fields = (
        ["benchmark", "runs", "population", "evaluations", "note"]
        + [f"{m}_{s}" for m in ("hv", "igd", "gd", "spacing")
           for s in ("mean", "std")]
    )

    with (RESULTS / "all_benchmarks_summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()

        for row in summary_rows:
            row = dict(row)
            row["evaluations"] = evaluations[row["benchmark"]]
            row["population"] = population[row["benchmark"]]
            row["note"] = NOTES.get(row["benchmark"], "")
            writer.writerow({k: row.get(k, "") for k in fields})

    print("Benchmarks combined:", len(summary_rows), "of", len(ALL_30))


if __name__ == "__main__":
    main()
