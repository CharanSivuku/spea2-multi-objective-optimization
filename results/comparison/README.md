# Comparison-ready results (SPEA2)

Derived from the final result files (`experiments/export_comparison.py`); nothing was
rerun. Use these files to put another algorithm on the same footing as SPEA2.

| File | Content |
|---|---|
| `spea2_runs.csv` | one row per run: `problem, algorithm, seed, HV, IGD, GD, spacing, runtime_seconds, evaluations` (30 problems x 5 seeds) |
| `spea2_summary.csv` | mean and standard deviation (sample, n - 1) per problem |
| `spea2_mmo_runs.csv`, `spea2_mmo_summary.csv` | CEC 2020 MMO (3 seeds): the competition indicators `rPSP` (1/PSP), `rHV` (1/HV), `IGDX`, `IGDF`, plus the objective-space indicators in the standard layout: `HV`, `IGD` (= IGDF), `GD`, `spacing` |
| `hv_reference_points.csv` | the hypervolume reference point used for every problem |
| `reference_fronts/<problem>.csv` | the reference front used for IGD, GD and the HV reference point |

## Definitions that must match for the numbers to be comparable

* **Shared run configuration** (seeds 1-5; population 100 / 1,000 generations /
  100,100 evaluations for ZDT and the 18 classical problems; population 200 /
  3,000 generations / 600,200 evaluations for DTLZ1-7; MMO: seeds 1-3, population 100,
  20,100 evaluations).
* **Scored set:** the non-dominated feasible solutions of the final archive / population.
* **HV:** exact hypervolume of that set (minimisation) w.r.t. the point in
  `hv_reference_points.csv`: per objective `max(reference front) + max(0.1, 0.1 * (max - min))`.
* **IGD** = mean over reference-front points of the Euclidean distance to the nearest obtained point.
* **GD** = sqrt( (1/|A|) * sum over obtained points of d^2 ), d = distance to the nearest
  reference-front point (root mean square; **not** the sqrt(sum d^2) / |A| form).
* **Spacing** = population standard deviation (divide by n) of the Euclidean
  nearest-neighbour distances within the obtained set.
* **Standard deviation across runs** = sample standard deviation (n - 1).
* **Runtime** is wall-clock seconds per run on a shared machine with 10 runs executing in
  parallel (Apple silicon, Python 3.9, NumPy); it is only comparable if hardware and
  software are documented and aligned.

If another algorithm's metrics were computed with different definitions, recompute them
from its final fronts with the reference fronts and reference points above.
