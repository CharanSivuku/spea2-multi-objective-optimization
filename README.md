# SPEA2 Multi-Objective Optimization

A from-scratch Python implementation of **SPEA2** (Strength Pareto Evolutionary
Algorithm 2), evaluated on a suite of **30 standard multi-objective benchmark
problems** (5 ZDT, 7 DTLZ, 18 classical) with four performance metrics
(Hypervolume, IGD, GD, Spacing), reproducible seeded runs, analytical or
documented numerical reference Pareto fronts, and optional constraint handling.
The repository also contains ports of two CEC competition suites: the **CEC 2022
single-objective** functions (12 problems) and the **CEC 2020 multimodal
multi-objective** problems (24 problems), each with the organisers' data,
protocol and indicators.

```
Algorithm  →  30 benchmarks  →  seeded independent runs  →  HV / IGD / GD / Spacing
          →  mean ± std per benchmark  →  figures, CSVs, report
```

> **Read this first:** the result sets in this repository were run with
> *different generation budgets* (250, 500 and 2000). Only compare numbers that
> share the same `Gens` value. See [Results](#results) and
> [Known limitations](#known-limitations).

---

## Contents

1. [Quick start](#quick-start)
2. [Project structure](#project-structure)
3. [Algorithm](#algorithm)
4. [Benchmark suite (30 problems)](#benchmark-suite-30-problems)
5. [Experimental protocol](#experimental-protocol)
6. [Metrics](#metrics)
7. [Results](#results)
8. [CEC competition suites](#cec-competition-suites)
9. [Corrections made during verification](#corrections-made-during-verification)
10. [Known limitations](#known-limitations)
11. [Reproducibility and testing](#reproducibility-and-testing)

---

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the tests (300 tests):

```bash
python -m pytest
```

Run benchmarks (any of the 30 registered names; results go to
`results/data/new_run/` unless `--output-dir` is given, and existing files are
never overwritten without `--overwrite`):

```bash
python experiments/run_benchmarks.py --benchmarks ZDT1 Tanaka DTLZ2 \
  --population 100 --archive 100 --generations 250 --runs 10 \
  --seed-start 1 --output-dir results/data/my_run
```

Rebuild the combined table `results/all_benchmarks_summary.csv` from the
organised result sets:

```bash
python experiments/merge_results.py
```

Runner options: `--benchmarks`, `--population`, `--archive`, `--generations`,
`--runs`, `--seed-start`, `--dtlz-vars` (default 12), `--objectives` (default 3),
`--output-dir`, `--overwrite`.

The two CEC suites have their own runners (details in
[CEC competition suites](#cec-competition-suites)):

```bash
python experiments/run_cec2020_mmo.py --workers 8 --output-dir results/data/my_mmo_run
python experiments/run_cec2022.py --functions 1 2 3 --dims 10 --workers 8 --output-dir results/data/my_cec2022_run
```

---

## Project structure

```
spea2-multi-objective/
├── src/
│   ├── spea2.py                 SPEA2 (+ opt-in constraint dominance) and the ZDT functions
│   ├── benchmarks/
│   │   ├── dtlz.py              DTLZ1-7 and their reference fronts
│   │   ├── classical.py         Binh1, Deb, Deb2, Fonseca, Fonseca2, Kursawe
│   │   ├── classical_extra.py   Binh3, Laumanns, Murata, Quagliarella, Rendon, Rendon2,
│   │   │                        Schaffer, Schaffer2, Srinivas, Tanaka, Viennet, Viennet2
│   │   ├── cec2022.py           CEC 2022 single-objective suite (F1-F12), port of the C reference
│   │   └── cec2020_mmo.py       CEC 2020 multimodal multi-objective suite (24 problems)
│   └── metrics/                 hypervolume.py, igd.py, gd.py, spacing.py,
│                                mmo.py (IGDX, cover rate, PSP, 1/HV for the MMO suite)
├── data/                        official CEC 2022 / CEC 2020 MMO input data (see data/README.md)
├── experiments/
│   ├── benchmark_registry.py    central registry of all 30 benchmarks
│   ├── run_benchmarks.py        experiment runner (CSV + figures)
│   ├── merge_results.py         builds results/all_benchmarks_summary.csv
│   ├── run_cec2022.py           CEC 2022 runner (30 runs, checkpoints, official seeds)
│   ├── run_cec2020_mmo.py       CEC 2020 MMO runner (21 runs, 1/PSP, 1/HV, IGDX, IGDF)
│   ├── plot_front.py            2-D / 3-D Pareto-front plots
│   ├── plot_mmo.py              Pareto set + front plots for the MMO problems
│   ├── zdt_benchmarks.py        legacy ZDT-only script (250 generations)
│   ├── zdt1_experiment.py       legacy single-problem script
│   └── test_classical.py        older registry test (not collected by pytest)
├── tests/                       metrics, DTLZ, classical_extra, constraints, spea2_regression, cec2022, cec2020_mmo
├── results/                     all outputs, organised (see results/README.md)
├── validate_dtlz.py             quick DTLZ sanity prints
├── pytest.ini
└── requirements.txt
```

### Results folder

```
results/
├── README.md                    guide to the folder
├── all_benchmarks_summary.csv   one row per benchmark (30)
├── MANIFEST.tsv                 old → new location of every file
├── figures/                     all 30 figures (one PNG per benchmark), _overview_all_30.png, archive/
├── data/                        raw + summary CSVs, one numbered folder per run set
├── reports/                     written reports
└── logs/                        console output of runs
```

---

## Algorithm

SPEA2 is implemented directly in `src/spea2.py` with no optimisation library.
Each generation works on the union of the population and the archive:

| Step | Definition |
|---|---|
| Strength | `S(i) = number of solutions that i dominates` |
| Raw fitness | `R(i) = Σ S(j)` over all `j` that dominate `i` (0 for non-dominated) |
| Density | `D(i) = 1 / (σ_k(i) + 2)`, with `k = max(1, ⌊√N⌋)` and `N` the union size |
| Fitness | `F(i) = R(i) + D(i)`; lower is better |
| Environmental selection | keep solutions with `F < 1`; truncate by lexicographic nearest-neighbour distances if there are too many, otherwise fill with the best remaining by fitness |
| Parent selection | binary tournament on fitness |
| Crossover | SBX, probability 0.9, distribution index 20, clipped to bounds |
| Mutation | polynomial, probability `1/n`, index 20, clipped to bounds |

The archive is padded with the best dominated solutions when fewer than the
archive size are non-dominated, so a final archive can contain dominated points.

### Performance optimisations (results unchanged)

The pairwise parts of SPEA2 (dominance, strength, raw fitness, distance matrix,
density, archive truncation) are vectorised with NumPy, and the archive's
objective values are cached instead of being recomputed every generation. The
original pure-Python versions are kept as `*_reference` functions in
`src/spea2.py`, and `tests/test_spea2_regression.py` checks that the fast versions
return **exactly** the same values and removals (including ties, duplicates and
constraints) and that complete SPEA2 runs give identical output to the
pre-optimisation code. Two details matter for exactness: distances use
`np.power(d, 2.0)` because Python's `x ** 2` differs from `x * x` in the last bit
for about 0.1 % of floats, and each solution is now evaluated exactly once, which
makes evaluation budgets exact. The speed-up is large (the 3-objective MMO
problem with population 800 went from hours per run to under 20 s), so
experiments run with this code finish faster but are numerically identical to the
earlier ones.

### Constraint handling (opt-in)

`spea2(..., constraint_function=None)` accepts a function returning the *total
constraint violation* (0 = feasible, > 0 = infeasible). When given, dominance is
feasibility-first (Deb's constraint dominance):

1. a feasible solution dominates any infeasible one;
2. between two infeasible solutions the smaller violation dominates;
3. between two feasible solutions ordinary Pareto dominance applies.

With `constraint_function=None` the algorithm is bit-identical to the original
unconstrained SPEA2 (covered by a test). The runner scores only feasible archive
members. Srinivas and Tanaka are the constrained benchmarks.

---

## Benchmark suite (30 problems)

All objectives are minimised. Every benchmark is registered in
`experiments/benchmark_registry.py` with its objective function, dimensions,
bounds, reference front and (if any) constraint function.

| # | Benchmark | Vars | Obj | Bounds | Constrained | Reference front |
|---|---|---:|---:|---|:---:|---|
| 1 | ZDT1 | 30 | 2 | [0, 1] | – | analytical |
| 2 | ZDT2 | 30 | 2 | [0, 1] | – | analytical |
| 3 | ZDT3 | 30 | 2 | [0, 1] | – | analytical (5 intervals) |
| 4 | ZDT4 | 10 | 2 | x1 ∈ [0,1], rest [−5,5] | – | analytical |
| 5 | ZDT6 | 10 | 2 | [0, 1] | – | analytical |
| 6–12 | DTLZ1 … DTLZ7 | 12 | 3 | [0, 1] | – | analytical geometry (DTLZ7: sampled on g=1, non-dominated) |
| 13 | Binh1 | 2 | 2 | [−5, 10] | – | analytical |
| 14 | Binh3 | 2 | 3 | [1e-6, 1e6] | – | single ideal point |
| 15 | Deb | 2 | 2 | [0, 1] | – | analytical |
| 16 | Deb2 | 2 | 2 | [0, 1] | – | non-dominated part of the x2 = 0 curve |
| 17 | Fonseca | 2 | 2 | [−4, 4] | – | parametric |
| 18 | Fonseca2 | 2 | 2 | [−4, 4] | – | parametric |
| 19 | Kursawe | 3 | 2 | [−5, 5] | – | sampled (41 pts, coarse) |
| 20 | Laumanns | 2 | 2 | [−50, 50] | – | analytical |
| 21 | Murata | 2 | 2 | x1 ∈ [1,4], x2 ∈ [1,2] | – | analytical |
| 22 | Quagliarella | 16 | 2 | [−5.12, 5.12] | – | numerical: exact DP Minkowski sum |
| 23 | Rendon | 2 | 2 | [−3, 3] | – | analytical |
| 24 | Rendon2 | 2 | 2 | [−3, 3] | – | analytical |
| 25 | Schaffer | 1 | 2 | [−10, 10] | – | analytical |
| 26 | Schaffer2 | 1 | 2 | [−5, 10] | – | analytical (2 segments) |
| 27 | Srinivas | 2 | 2 | [−20, 20] | **2** | numerical: Pareto-set candidates, ND-filtered |
| 28 | Tanaka | 2 | 2 | [0, π] | **2** | numerical: constraint boundaries, ND-filtered |
| 29 | Viennet | 2 | 3 | [−2, 2] | – | analytical (triangle Pareto set) |
| 30 | Viennet2 | 2 | 3 | [−4, 4] | – | numerical: weighted-sum minimisers (convex) |

The 12 benchmarks in `classical_extra.py` follow the MOEA Framework
`problem.misc` formulations (Van Veldhuizen's suite) and were checked against
the value ranges in `Benchmark_Comparison.pdf`. No reference front was produced
by random sampling of the decision space except Kursawe's older, coarse one.
Details and caveats: `results/reports/classical_benchmarks_report.md`.

---

## Experimental protocol

| Parameter | Value |
|---|---|
| Population size | 100 |
| Archive size | 100 |
| Independent runs | 10 (seeds 1–10; DTLZ1/3/6 old set: 5) |
| Crossover | SBX, probability 0.9, η = 20 |
| Mutation | polynomial, probability 1/n, η = 20 |
| DTLZ | 12 variables, 3 objectives, 50 reference divisions |

Runner NFE per run: `100 + (G − 1)·200` for `G` generations
(250 → 49,900; 500 → 99,900; 2000 → 399,900). The legacy ZDT script counts
`100 + G·100` instead (250 → 25,100).

### Result sets and generation budgets

| Set (`results/data/`) | Benchmarks | Runs | Gens |
|---|---|---:|---:|
| `01_zdt_500gen` | ZDT1/2/3/4/6 (runner, 10-variable ZDT4) | 10 | 500 |
| `01_zdt_500gen/raw_metrics.csv` | ZDT1/2/3/4/6 (legacy script, 30-variable ZDT4) | 10 | 250 |
| `02_dtlz1-3-6_2000gen` | DTLZ1, DTLZ3, DTLZ6 | 5 | 2000 |
| `03_dtlz2-4-5-7_and_classical6_250gen` | DTLZ2/4/5/7, Binh1, Deb, Deb2, Fonseca, Fonseca2, Kursawe | 10 | 250 |
| `04_dtlz6_250gen_rerun` | DTLZ6 (corrected reference) | 10 | 250 |
| `05_classical12_new_250gen` | the 12 benchmarks in `classical_extra.py` | 10 | 250 |

---

## Metrics

| Metric | Meaning | Better |
|---|---|---|
| Hypervolume (HV) | volume dominated by the approximation up to a reference point | higher |
| IGD | mean distance from each reference-front point to its nearest obtained point (convergence + coverage) | lower |
| GD | RMS distance from each obtained point to its nearest reference-front point (convergence) | lower |
| Spacing | standard deviation of nearest-neighbour distances (uniformity) | lower |

The runner chooses the HV reference point per benchmark as the maximum of the
reference front in each objective plus a margin of `max(0.1, 10 % of the range)`
(for ZDT1 this is `[1.1, 1.1]`). HV values are therefore comparable across
algorithms on the *same* benchmark, not across benchmarks. The legacy ZDT script
used a fixed `[1.1, 1.1]`, which is why its ZDT3 HV differs from the runner's.

Metrics are computed on the final archive (feasible members only for constrained
problems). Runs with no feasible solution would be recorded as NaN; none occurred.

---

## Results

Mean ± standard deviation over the runs. **Compare only rows with equal `Gens`.**
Generated from `results/all_benchmarks_summary.csv`.

| Benchmark | Runs | Gens | HV ↑ | IGD ↓ | GD ↓ | Spacing ↓ | Note |
|---|---:|---:|---|---|---|---|---|
| ZDT1 | 10 | 500 | 0.8706 ± 0.00015 | 0.004177 ± 6.8e-05 | 0.002081 ± 0.0002 | 0.002296 ± 0.0002 |  |
| ZDT2 | 10 | 500 | 0.5377 ± 0.00018 | 0.003995 ± 4e-05 | 0.0009676 ± 0.00021 | 0.002255 ± 0.00018 |  |
| ZDT3 | 10 | 500 | 1.124 ± 0.00013 | 0.004902 ± 9.3e-05 | 0.0009639 ± 0.00012 | 0.003301 ± 0.00041 |  |
| ZDT4 | 10 | 500 | 0.8698 ± 0.0012 | 0.004301 ± 0.00042 | 0.002224 ± 0.00054 | 0.002136 ± 0.00023 |  |
| ZDT6 | 10 | 500 | 0.4375 ± 0.00033 | 0.003774 ± 0.00015 | 0.001859 ± 0.00024 | 0.001767 ± 0.00014 |  |
| DTLZ1 | 5 | 2000 | 0.1867 ± 0.0014 | 0.02508 ± 0.0037 | 0.9476 ± 1.8 | 0.7139 ± 1.5 | 5 runs; 2000 generations |
| DTLZ2 | 10 | 250 | 0.7201 ± 0.0029 | 0.05699 ± 0.00088 | 0.02386 ± 0.0034 | 0.01449 ± 0.0022 |  |
| DTLZ3 | 5 | 2000 | 0.7299 ± 0.0052 | 0.05445 ± 0.0025 | 0.1268 ± 0.14 | 0.08565 ± 0.13 | 5 runs; 2000 generations |
| DTLZ4 | 10 | 250 | 0.644 ± 0.13 | 0.1716 ± 0.18 | 0.01944 ± 0.0073 | 0.01053 ± 0.0051 |  |
| DTLZ5 | 10 | 250 | 0.1507 ± 0.00022 | 0.004515 ± 0.00051 | 0.009513 ± 0.00024 | 0.002687 ± 0.00035 |  |
| DTLZ6 | 10 | 250 | 0 ± 0 | 1.386 ± 0.062 | 1.932 ± 0.16 | 0.1078 ± 0.026 | 250 generations did not converge (HV 0); old 2000-gen result used a wrong reference front |
| DTLZ7 | 10 | 250 | 1.418 ± 0.068 | 0.09322 ± 0.089 | 0.1081 ± 0.051 | 0.0315 ± 0.011 |  |
| Binh1 | 10 | 250 | 2597 ± 0.43 | 0.2223 ± 0.0025 | 0.06278 ± 0.012 | 0.1404 ± 0.022 |  |
| Binh3 | 10 | 250 | 0.001 ± 0 | 0 ± 0 | 0 ± 0 | 0 ± 0 | single-point front; HV is only the reference-point margin |
| Deb | 10 | 250 | 0.5385 ± 3.1e-05 | 0.003919 ± 5.2e-05 | 0.0004595 ± 2.6e-05 | 0.002367 ± 0.00018 |  |
| Deb2 | 10 | 250 | 0.8346 ± 5.5e-05 | 0.004472 ± 0.00012 | 0.003058 ± 0.0043 | 0.003885 ± 0.0035 |  |
| Fonseca | 10 | 250 | 0.2714 ± 6.6e-05 | 0.004659 ± 7e-05 | 0.001002 ± 0.00015 | 0.00282 ± 0.00039 |  |
| Fonseca2 | 10 | 250 | 0.5065 ± 0.0002 | 0.004023 ± 9.1e-05 | 0.001494 ± 0.00023 | 0.002213 ± 0.00018 |  |
| Kursawe | 10 | 250 | 41.1 ± 0.012 | 0.1526 ± 0.0022 | 0.2417 ± 0.0031 | 0.08191 ± 0.00066 |  |
| Laumanns | 10 | 250 | 16.63 ± 0.00097 | 0.01682 ± 7.2e-05 | 0.002106 ± 0.00049 | 0.008305 ± 0.0007 |  |
| Murata | 10 | 250 | 3.894 ± 0.00055 | 0.00966 ± 0.00011 | 0.002605 ± 0.0022 | 0.005859 ± 0.00046 |  |
| Quagliarella | 10 | 250 | 8.767 ± 0.086 | 0.1727 ± 0.02 | 0.01144 ± 0.0012 | 0.008255 ± 0.001 | front extremes not reached (needs all 16 variables at 0 or 1.5) |
| Rendon | 10 | 250 | 38.94 ± 0.018 | 0.09268 ± 0.0026 | 0.01982 ± 0.0014 | 0.05633 ± 0.0068 |  |
| Rendon2 | 10 | 250 | 23.54 ± 0.0018 | 0.02553 ± 0.00046 | 0.003737 ± 0.00032 | 0.01489 ± 0.0011 |  |
| Schaffer | 10 | 250 | 16.63 ± 0.0012 | 0.01702 ± 0.00011 | 0.001823 ± 0.00011 | 0.00939 ± 0.00058 |  |
| Schaffer2 | 10 | 250 | 25.98 ± 0.0018 | 0.02279 ± 0.00054 | 0.00362 ± 0.00011 | 0.01298 ± 0.0016 |  |
| Srinivas | 10 | 250 | 3.492e+04 ± 8.7 | 0.8674 ± 0.016 | 0.3102 ± 0.056 | 0.5198 ± 0.072 |  |
| Tanaka | 10 | 250 | 0.5122 ± 0.00032 | 0.004212 ± 0.00032 | 0.002047 ± 0.00014 | 0.003013 ± 0.00051 |  |
| Viennet | 10 | 250 | 32.42 ± 0.035 | 0.1282 ± 0.0045 | 0.1382 ± 0.019 | 0.0393 ± 0.0037 |  |
| Viennet2 | 10 | 250 | 0.8389 ± 0.00041 | 0.01226 ± 0.00071 | 0.01793 ± 0.0017 | 0.005969 ± 0.00051 |  |

### What the results show

* **Converged well:** ZDT1/2/3/4/6 at 500 generations, Deb, Fonseca, Fonseca2,
  Laumanns, Murata, Rendon2, Schaffer, Schaffer2, Tanaka, Viennet2, DTLZ5, Deb2
  (IGD ≈ 0.004–0.03 with tiny run-to-run variation).
* **Hard at the budgets used:** DTLZ6 (250 generations: HV 0), DTLZ4 and DTLZ7
  (large run-to-run variance at 250), Quagliarella (the extremes of the front
  need all 16 variables at exactly 0 or 1.5), Kursawe and Rendon/Viennet (sparse
  coverage of extremes, IGD ≈ 0.1–0.15).
* **Binh3:** the true front is one point (x1 = x2 = 1e-6). All runs reached it
  (IGD = GD = 0); its HV is just the 0.1 reference-point margin and carries no
  information.
* **Srinivas** values are in the units of a front spanning f1 ∈ [10, 225], so
  IGD 0.87 is ≈ 0.4 % of the front length; its HV is not comparable with other
  problems.

### Legacy ZDT results at 250 generations (PESA-II protocol)

Produced by `experiments/zdt_benchmarks.py` (population/archive 100,
250 generations, seeds 1–10, ZDT4 with 30 variables, fixed HV reference
`[1.1, 1.1]`); stored in `results/data/01_zdt_500gen/raw_metrics.csv`.

| Benchmark | HV ↑ | IGD ↓ | GD ↓ | Spacing ↓ |
|---|---|---|---|---|
| ZDT1 | 0.868337 ± 0.000633 | 0.004843 ± 0.000267 | 0.002902 ± 0.000373 | 0.002299 ± 0.000146 |
| ZDT2 | 0.535224 ± 0.000355 | 0.004603 ± 0.000135 | 0.002260 ± 0.000244 | 0.002328 ± 0.000304 |
| ZDT3 | 1.315779 ± 0.025962 | 0.010841 ± 0.017632 | 0.002144 ± 0.000329 | 0.003464 ± 0.000393 |
| ZDT4 | 0.000000 ± 0.000000 | 4.241244 ± 1.832326 | 5.112376 ± 2.231289 | 0.592988 ± 1.158240 |
| ZDT6 | 0.491774 ± 0.001206 | 0.009988 ± 0.000822 | 0.009618 ± 0.000945 | 0.001935 ± 0.000209 |

Reported PESA-II baseline under the same protocol (for comparison only):

| Benchmark | HV ↑ | IGD ↓ | GD ↓ | Spacing ↓ |
|---|---|---|---|---|
| ZDT1 | 0.8605 ± 0.0023 | 0.0103 ± 0.0017 | 0.0015 ± 0.0003 | 0.0084 ± 0.0009 |
| ZDT2 | 0.5232 ± 0.0033 | 0.0110 ± 0.0012 | 0.0015 ± 0.0004 | 0.0078 ± 0.0011 |
| ZDT3 | 0.7167 ± 0.0091 | 0.0161 ± 0.0212 | 0.0006 ± 0.0002 | 0.0065 ± 0.0008 |
| ZDT4 | 0.8445 ± 0.0139 | 0.0262 ± 0.0203 | 0.2838 ± 0.4165 | 0.8271 ± 1.2527 |
| ZDT6 | 0.5908 ± 0.0262 | 0.0522 ± 0.0155 | 1.2607 ± 0.2148 | 0.3295 ± 0.3700 |

Against PESA-II at 250 generations, SPEA2 here has higher HV and lower IGD and
Spacing on ZDT1/2, lower IGD and Spacing on ZDT3 (the ZDT3 HV values are *not*
directly comparable because the HV reference policy has not been reconciled),
much lower IGD/GD/Spacing but lower HV on ZDT6, and does **not** converge on the
30-variable ZDT4 within 250 generations (HV 0). With 500 generations and the
10-variable ZDT4 of the runner set, ZDT4 converges (HV 0.870, IGD 0.0043).

---

## CEC competition suites

Two additional suites from the CEC competitions are included, with the
organisers' data (`data/`, see `data/README.md`) and evaluation protocol. Their
benchmarks are **not** part of the 30-problem registry or of
`all_benchmarks_summary.csv`.

### CEC 2020 multimodal multi-objective (24 problems)

`src/benchmarks/cec2020_mmo.py` ports MMF1, MMF2, MMF4, MMF5, MMF7, MMF8, MMF10-MMF15,
MMF1_e, MMF14_a, MMF15_a, the "local Pareto set" variants (MMF10_l, MMF11_l,
MMF12_l, MMF13_l, MMF15_l, MMF15_a_l) and MMF16_l1/l2/l3, with the organisers'
bounds, hypervolume reference points and number of Pareto sets (`N_ops`). The
reference Pareto sets and fronts are the organisers' data. A test checks that
the ported objective functions reproduce the reference fronts (row by row for 17
problems, as a set or on the analytic front for the others).

Protocol (`experiments/run_cec2020_mmo.py`): 21 runs, population = archive =
200 x N_ops, MaxFES = 10000 x N_ops (= 50 generations), indicators 1/PSP, 1/HV,
IGDX and IGDF (`src/metrics/mmo.py`). SPEA2 here is the project's SPEA2 with no
decision-space niching, so it is a baseline. Results of the full run (mean ± std
over 21 runs, all smaller-is-better):

| Problem | N_ops | 1/PSP | 1/HV | IGDX | IGDF |
|---|---:|---|---|---|---|
| MMF1 | 2 | 0.03774 ± 0.0047 | 1.143 ± 0.00012 | 0.0376 ± 0.0047 | 0.001203 ± 6.4e-05 |
| MMF2 | 2 | 0.02277 ± 0.0076 | 1.153 ± 0.003 | 0.02265 ± 0.0076 | 0.006122 ± 0.0016 |
| MMF4 | 2 | 0.02297 ± 0.0048 | 1.846 ± 0.0001 | 0.02284 ± 0.0047 | 0.001067 ± 7.4e-05 |
| MMF5 | 2 | 0.07027 ± 0.0083 | 1.143 ± 7.5e-05 | 0.07002 ± 0.0083 | 0.001189 ± 3.6e-05 |
| MMF7 | 2 | 0.02051 ± 0.0038 | 1.143 ± 3.8e-05 | 0.0204 ± 0.0038 | 0.001072 ± 2.8e-05 |
| MMF8 | 2 | 0.3148 ± 0.1 | 2.363 ± 0.00056 | 0.2831 ± 0.084 | 0.001077 ± 2.1e-05 |
| MMF10 | 1 | 0.03863 ± 0.11 | 0.07847 ± 0.0025 | 0.03862 ± 0.11 | 0.03651 ± 0.088 |
| MMF11 | 1 | 0.005335 ± 0.00034 | 0.06887 ± 4.2e-06 | 0.005334 ± 0.00034 | 0.01258 ± 0.00051 |
| MMF12 | 1 | 0.001505 ± 0.00015 | 0.6354 ± 2.4e-05 | 0.001505 ± 0.00015 | 0.001984 ± 8e-05 |
| MMF13 | 1 | 0.06882 ± 0.012 | 0.05426 ± 6.3e-06 | 0.0633 ± 0.009 | 0.01629 ± 0.00071 |
| MMF14 | 2 | 0.04752 ± 0.0032 | 0.1619 ± 0.00015 | 0.04749 ± 0.0032 | 0.05248 ± 0.0014 |
| MMF15 | 1 | 0.04141 ± 0.001 | 0.09191 ± 0.0001 | 0.04137 ± 0.001 | 0.07724 ± 0.0017 |
| MMF1_e | 2 | 3.382 ± 2.2 | 1.144 ± 0.00044 | 1.65 ± 0.62 | 0.001659 ± 0.00013 |
| MMF14_a | 2 | 0.0593 ± 0.0045 | 0.1623 ± 0.00014 | 0.0592 ± 0.0042 | 0.05432 ± 0.0013 |
| MMF15_a | 1 | 0.05164 ± 0.0011 | 0.09226 ± 0.00015 | 0.05161 ± 0.0011 | 0.08253 ± 0.0024 |
| MMF10_l | 2 | 2.949 ± 4.6 | 0.07763 ± 1.1e-06 | 0.1743 ± 0.019 | 0.1667 ± 0.019 |
| MMF11_l | 2 | 2.417 ± 0.61 | 0.06881 ± 1e-06 | 0.2496 ± 0.0055 | 0.08911 ± 0.0051 |
| MMF12_l | 2 | 3.064 ± 1 | 0.6352 ± 9.8e-06 | 0.2455 ± 0.003 | 0.07901 ± 0.0067 |
| MMF13_l | 2 | 0.6431 ± 0.22 | 0.0542 ± 2.1e-06 | 0.278 ± 0.022 | 0.1299 ± 0.019 |
| MMF15_l | 2 | 0.4553 ± 0.072 | 0.09071 ± 3.2e-05 | 0.2553 ± 0.0047 | 0.1727 ± 0.0034 |
| MMF15_a_l | 2 | 0.2482 ± 0.0092 | 0.09092 ± 4.3e-05 | 0.2026 ± 0.0044 | 0.1627 ± 0.0038 |
| MMF16_l1 | 3 | 0.1822 ± 0.016 | 0.08919 ± 2.6e-05 | 0.1477 ± 0.0035 | 0.1297 ± 0.003 |
| MMF16_l2 | 3 | 0.569 ± 0.11 | 0.08916 ± 3.3e-05 | 0.3219 ± 0.01 | 0.2195 ± 0.0064 |
| MMF16_l3 | 4 | 0.2489 ± 0.027 | 0.08894 ± 1.9e-05 | 0.1975 ± 0.0065 | 0.1677 ± 0.0039 |

Figures: `results/figures/mmf*.png` (obtained vs reference set and front).
Details, observations and data issues found in the organisers' settings:
`results/reports/cec2020_mmo_report.md`.

### CEC 2022 single-objective (12 functions)

`src/benchmarks/cec2022.py` is a line-by-line port of the organisers' C
reference (`cec22_test_func.cpp`) using the official shift / rotation / shuffle
data: F1-F5 basic (Zakharov, Rosenbrock, Expanded Schaffer, Rastrigin, Levy),
F6-F8 hybrid, F9-F12 composition, for D = 10 and 20, search range [-100, 100]^D.
The organisers' Python version was not used because it is not functional (it
calls an undefined function, among other problems). The C code's quirks are
reproduced and documented in the module: F3 ignores the rotation, F4's step
has no effect, Levy uses `sin(pi*w + 1)`, and the Schaffer F7 component of F7
reads its input from index 0. Every function equals its published optimum F*
at the shifted optimum (tested).

Protocol (`experiments/run_cec2022.py`): 30 runs with seeds from the official
`Rand_Seeds.txt`, MaxFES 200,000 (D = 10) / 1,000,000 (D = 20), stop at error
1e-8, best error recorded at the 16 checkpoints `floor(D^(k/5-3) * MaxFES)`
plus FEterm, and the 17 x 30 result files in the competition format. SPEA2 runs
with a single objective (Pareto dominance reduces to ranking) and is untuned.
**The full 12-function experiment has not been run yet**: a single run takes
about 12 s (F1, D = 10) up to about 70 s (composition F9, D = 10), and D = 20
runs with 1M evaluations take several times longer, so the full experiment is
roughly 15-20 CPU-hours.

---

## Corrections made during verification

Found while checking results against the true fronts; all fixed and covered by
regression tests. Affected earlier runs are kept in
`results/data/superseded_wrong_reference/` and `results/figures/archive/`.

| Problem | Error | Effect of the fix |
|---|---|---|
| Srinivas | first reference front covered only x1 = −2.5; the true Pareto set also lies on the constraint line and circle | front now spans f1 ∈ [10, 225]; rerun |
| Deb2 | reference was the whole x2 = 0 curve (~78 % dominated points) | IGD 0.185 → 0.0045; rerun |
| DTLZ5 / DTLZ6 | reference used angle 0.25 instead of 0.5, so f1 ≠ f2 (not on the true front) | DTLZ5 IGD 0.245 → 0.0045; rerun. DTLZ6 old 2000-gen result is **not trusted** |

---

## Known limitations

* **Mixed generation budgets** (250 / 500 / 2000) across result sets; compare
  within equal `Gens` only.
* **DTLZ6** has no reliable result: the old 2000-generation run used the wrong
  reference front, and the corrected 250-generation run did not converge.
* **DTLZ1 and DTLZ3** have 5 runs (2000 generations), not 10.
* The two ZDT sets differ in more than generations (ZDT4 has 30 variables in the
  legacy 250-generation set and 10 in the runner set).
* **Kursawe's** reference front has only 41 points, so its IGD is coarse.
  ZDT3's reference contains ~4 dominated points out of 1000 (negligible).
* **Numerical reference fronts** (Quagliarella, Srinivas, Tanaka, Viennet2) are
  accurate to roughly 0.002–0.005 in tests; they are not exact analytical fronts.
* **Schaffer** uses bounds [−10, 10]; the literature uses 10 up to 1e5.
  **Tanaka's** lower bound is 0 rather than strictly positive (`atan2` handles it).
* Mostly pure Python with NumPy-vectorised SPEA2 internals; the experiments in
  `results/` before the optimisation took roughly 20–180 s per 250-generation run,
  the same runs are now several times faster with identical results.
* **CEC 2022** has no results yet (full experiment not run, about 15-20 CPU-hours);
  SPEA2 is a multi-objective algorithm run here with a single objective.
* **CEC 2020 MMO:** SPEA2 has no decision-space niching, and the competition's budget
  is only 50 generations, so the results are a baseline. Several issues in the
  organisers' own data and settings (MMF13_l bounds, HV reference points of
  MMF12_l / MMF13_l, MMF2 boundary point, 2-objective-only MATLAB hypervolume)
  are replicated and documented in `results/reports/cec2020_mmo_report.md`.
* `experiments/zdt_benchmarks.py` still writes to `results/raw_metrics.csv` if
  re-run; use `run_benchmarks.py --output-dir` instead.

---

## Reproducibility and testing

* Seeds are `seed_start … seed_start + runs − 1` (default 1–10) and are stored in
  every raw CSV row, together with runtime, archive size and NFE.
* Existing result files are never overwritten by the runner without `--overwrite`.
* `python -m pytest` runs 300 tests: metrics, DTLZ functions, objective values at
  hand-computed points, bounds and dimensions of the 12 added classical
  benchmarks, reference-front validity (finite, non-dominated, not beaten by random
  feasible samples, brute-force comparison for Srinivas), constraint dominance,
  tiny SPEA2 smoke runs, **exact equivalence of the optimised SPEA2 code with the
  original pure-Python code** (random cases and full-run digests), the CEC 2022
  suite (F(o) = F*, official-data checksums, group sizes, seeds, budget and
  checkpoint tracking) and the CEC 2020 MMO suite (objective vs reference front,
  indicators, runner).
* Exact reproduction needs the same Python and NumPy versions (see
  `requirements.txt`).

---

## License

This project is intended for educational use.
