"""Build results/all_benchmarks_summary.csv from the organised result sets.

Reads (never modifies) the summary and raw CSVs under results/data/, and writes
only results/all_benchmarks_summary.csv. For every benchmark it records the
run count, the number of generations (derived from the NFE column of the raw
file), the source set, and a note for results that need care.

Layout it expects (see results/README.md):
  results/data/01_zdt_500gen/
  results/data/02_dtlz1-3-6_2000gen/
  results/data/03_dtlz2-4-5-7_and_classical6_250gen/
  results/data/04_dtlz6_250gen_rerun/
  results/data/05_classical12_new_250gen/
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = RESULTS / "data"

ALL_30 = (
    ["ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6"]
    + [f"DTLZ{i}" for i in range(1, 8)]
    + ["Binh1", "Binh3", "Deb", "Deb2", "Fonseca", "Fonseca2", "Kursawe",
       "Laumanns", "Murata", "Quagliarella", "Rendon", "Rendon2",
       "Schaffer", "Schaffer2", "Srinivas", "Tanaka", "Viennet", "Viennet2"]
)

# Later sets override earlier ones for the same benchmark.
SETS = [
    "01_zdt_500gen",
    "02_dtlz1-3-6_2000gen",
    "03_dtlz2-4-5-7_and_classical6_250gen",
    "05_classical12_new_250gen",
    "04_dtlz6_250gen_rerun",
]

NOTES = {
    "DTLZ1": "5 runs; 2000 generations",
    "DTLZ3": "5 runs; 2000 generations",
    "DTLZ6": "250 generations did not converge (HV 0); old 2000-gen "
             "result used a wrong reference front",
    "Binh3": "single-point front; HV is only the reference-point margin",
    "Quagliarella": "front extremes not reached (needs all 16 variables "
                    "at 0 or 1.5)",
}


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def generations_from_nfe(nfe, population=100, archive=100):
    return round((nfe - population) / (population + archive) + 1)


def main():
    found = {}

    for name in SETS:
        folder = DATA / name
        raw = read_rows(folder / "raw_metrics_all.csv")
        gens = {}

        for row in raw:
            gens[row["benchmark"]] = generations_from_nfe(float(row["nfe"]))

        for row in read_rows(folder / "summary_metrics_all.csv"):
            found[row["benchmark"]] = dict(
                row,
                source=f"data/{name}",
                generations=gens[row["benchmark"]],
            )

    fields = (
        ["benchmark", "runs", "generations", "source", "note"]
        + [f"{m}_{s}" for m in ("hv", "igd", "gd", "spacing")
           for s in ("mean", "std")]
    )

    with (RESULTS / "all_benchmarks_summary.csv").open(
        "w", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()

        for name in ALL_30:
            row = found.get(name)

            if row is None:
                writer.writerow(
                    {"benchmark": name, "source": "NO METRICS CSV"}
                )
                continue

            row["note"] = NOTES.get(name, "")
            writer.writerow({k: row.get(k, "") for k in fields})

    missing = [n for n in ALL_30 if n not in found]
    print("Benchmarks with metrics:", len(found), "of", len(ALL_30))
    print("Missing:", ", ".join(missing) or "none")


if __name__ == "__main__":
    main()
