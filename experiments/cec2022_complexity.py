"""Algorithm-complexity measurement of the CEC 2022 technical report (section 2.2, item 4).

* T0: time of the reference loop below (200,000 iterations).
* T1: time of 200,000 evaluations of function F1 at dimension D.
* T2: mean over 5 complete runs of the algorithm (SPEA2) doing 200,000
  evaluations of F1 at dimension D.
* Reported: T0, T1, T2 and (T2 - T1) / T0 for D = 10 and 20.

All three timings use the same programming style (single-threaded Python,
one solution evaluated at a time). Run it on an otherwise idle machine.

    x = 0.55
    for i in 1..200000:
        x = x + x; x = x / 2; x = x * x; x = sqrt(x); x = log(x); x = exp(x); x = x / (x + 2)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.run_cec2022 import run_once  # noqa: E402
from src.benchmarks.cec2022 import CEC2022Function  # noqa: E402

EVALUATIONS = 200_000


def time_t0() -> float:
    started = time.perf_counter()
    x = 0.55

    for _ in range(EVALUATIONS):
        x = x + x
        x = x / 2
        x = x * x
        x = math.sqrt(x)
        x = math.log(x)
        x = math.exp(x)
        x = x / (x + 2)

    return time.perf_counter() - started


def time_t1(dim: int) -> float:
    function = CEC2022Function(1, dim)
    rng = random.Random(0)
    points = [
        [rng.uniform(-100, 100) for _ in range(dim)] for _ in range(1000)
    ]

    started = time.perf_counter()

    for i in range(EVALUATIONS):
        function(points[i % 1000])

    return time.perf_counter() - started


def time_t2(dim: int, repeats: int = 5) -> list:
    times = []

    for repeat in range(repeats):
        started = time.perf_counter()
        # (function 1, run id = repeat + 1, 30 runs, population 100, archive 100)
        result = run_once((1, dim, repeat + 1, 30, 100, 100, EVALUATIONS))
        times.append(time.perf_counter() - started)

        assert result["fe_term"] == EVALUATIONS, "run stopped early"

    return times


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    out = (
        Path(args.output_dir).resolve() if args.output_dir
        else ROOT / "results" / "data" / "07_cec2022_30runs"
    )
    out.mkdir(parents=True, exist_ok=True)
    csv_file = out / "complexity.csv"
    info_file = out / "complexity_system.json"

    if csv_file.exists() and not args.overwrite:
        parser.error(f"{csv_file} exists (use --overwrite)")

    t0 = min(time_t0() for _ in range(3))
    rows = []

    for dim in (10, 20):
        t1 = time_t1(dim)
        t2_runs = time_t2(dim)
        t2 = sum(t2_runs) / len(t2_runs)
        rows.append({
            "D": dim,
            "T0": t0,
            "T1": t1,
            "T2": t2,
            "(T2-T1)/T0": (t2 - t1) / t0,
        })
        print(
            f"D={dim}: T0={t0:.3f}s  T1={t1:.3f}s  T2={t2:.3f}s  "
            f"(T2-T1)/T0={(t2 - t1) / t0:.1f}",
            flush=True,
        )

    with csv_file.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    info_file.write_text(json.dumps({
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "t2_note": "mean of 5 complete SPEA2 runs (population 100, archive 100) of 200,000 evaluations of F1",
    }, indent=2))


if __name__ == "__main__":
    main()
