# SPEA2 on the standard benchmark suite (teammate protocol)

Final run of all 30 benchmarks under the configuration shared with the NSGA-II
baseline: **5 independent runs per problem, seeds 1-5**, uniform random
initialisation within the bounds.

| Problems | Population = archive | Generations | Evaluations / run | Variables |
|---|---:|---:|---:|---|
| ZDT1-3 | 100 | 1,000 | 100,100 | 30 |
| ZDT4, ZDT6 | 100 | 1,000 | 100,100 | 10 |
| DTLZ1-7 (3 objectives) | **200** | **3,000** | **600,200** | 12 |
| 18 classical problems | 100 | 1,000 | 100,100 | as defined |

"Generations" count offspring batches after the initial population, so the code
runs 1001 (or 3001 for DTLZ) iterations: 100 + 1000 x 100 = 100,100 evaluations
(200 + 3000 x 200 = 600,200 for DTLZ). Every solution is evaluated exactly once.

SPEA2 operators: SBX (probability 0.9 per parent pair, 0.5 per variable, eta 20)
and polynomial mutation (probability 1/n; eta 20, and **10 for DTLZ1-7** to mirror
the NSGA-II baseline), SPEA2 strength / raw-fitness / k-nearest-neighbour density
fitness, binary tournament on SPEA2 fitness, archive truncation by nearest-neighbour
distances. Constrained problems (Srinivas, Tanaka) use feasibility-first dominance.

**Scored set:** the non-dominated feasible solutions of the final archive. HV uses a
reference point 10 % (at least 0.1) beyond the reference front's maximum in every
objective. Metrics: HV (maximise), IGD, GD, Spacing (minimise).

Data: `results/data/standard_suite_team_protocol/` (`raw_metrics_all.csv` with one
row per run incl. seed and runtime, `summary_metrics_all.csv`, `per_benchmark/`);
combined table `results/all_benchmarks_summary.csv`; figures `results/figures/<name>.png`.

## Results (mean ± std over 5 runs)

| Benchmark | Pop | Evaluations | HV ↑ | IGD ↓ | GD ↓ | Spacing ↓ | Note |
|---|---:|---:|---|---|---|---|---|
| ZDT1 | 100 | 100,100 | 0.8717 ± 6e-05 | 0.003877 ± 5.8e-06 | 0.001611 ± 0.00011 | 0.002115 ± 0.00015 |  |
| ZDT2 | 100 | 100,100 | 0.5385 ± 4.9e-05 | 0.003893 ± 5.3e-05 | 0.0007426 ± 0.00028 | 0.002079 ± 0.00017 |  |
| ZDT3 | 100 | 100,100 | 1.125 ± 7e-05 | 0.00484 ± 4.7e-05 | 0.0008746 ± 0.00015 | 0.00321 ± 0.00041 |  |
| ZDT4 | 100 | 100,100 | 0.8716 ± 0.0001 | 0.003862 ± 6.8e-05 | 0.001578 ± 0.00011 | 0.001977 ± 0.0002 |  |
| ZDT6 | 100 | 100,100 | 0.4393 ± 4.7e-05 | 0.003142 ± 1.6e-05 | 0.0005915 ± 2e-05 | 0.001623 ± 0.00015 |  |
| DTLZ1 | 200 | 600,200 | 0.1915 ± 3.3e-05 | 0.01375 ± 0.00013 | 0.6501 ± 1.4 | 0.6295 ± 1.3 |  |
| DTLZ2 | 200 | 600,200 | 0.7541 ± 0.0016 | 0.03896 ± 0.00065 | 0.02184 ± 0.0057 | 0.01049 ± 0.0016 |  |
| DTLZ3 | 200 | 600,200 | 0.7647 ± 0.00095 | 0.03597 ± 0.00032 | 0.1866 ± 0.3 | 0.1725 ± 0.28 |  |
| DTLZ4 | 200 | 600,200 | 0.7561 ± 0.0019 | 0.03872 ± 0.001 | 0.01911 ± 0.0014 | 0.008446 ± 0.00079 |  |
| DTLZ5 | 200 | 600,200 | 0.1524 ± 2.2e-05 | 0.002075 ± 0.00013 | 0.009093 ± 3.5e-05 | 0.001101 ± 9.1e-05 |  |
| DTLZ6 | 200 | 600,200 | 0.1286 ± 0.0081 | 0.0352 ± 0.012 | 0.04131 ± 0.012 | 0.002472 ± 0.0002 |  |
| DTLZ7 | 200 | 600,200 | 1.514 ± 0.0034 | 0.03948 ± 0.00065 | 0.05912 ± 0.024 | 0.02306 ± 0.013 |  |
| Binh1 | 100 | 100,100 | 2597 ± 0.26 | 0.2208 ± 0.0032 | 0.05778 ± 0.01 | 0.1297 ± 0.012 |  |
| Binh3 | 100 | 100,100 | 0.001 ± 0 | 0 ± 0 | 0 ± 0 | 0 ± 0 | single-point front; HV is only the reference-point margin |
| Deb | 100 | 100,100 | 0.5385 ± 5.7e-05 | 0.00388 ± 2.5e-05 | 0.0004508 ± 9.8e-06 | 0.002399 ± 0.0002 |  |
| Deb2 | 100 | 100,100 | 0.8347 ± 8e-05 | 0.004512 ± 0.00013 | 0.001711 ± 0.0001 | 0.002474 ± 0.00029 |  |
| Fonseca | 100 | 100,100 | 0.2714 ± 8.5e-05 | 0.004753 ± 0.00019 | 0.00105 ± 0.00025 | 0.003353 ± 0.00074 |  |
| Fonseca2 | 100 | 100,100 | 0.5065 ± 0.00012 | 0.004002 ± 0.00012 | 0.001478 ± 0.00017 | 0.002064 ± 0.00022 |  |
| Kursawe | 100 | 100,100 | 41.14 ± 0.007 | 0.1541 ± 0.0027 | 0.2417 ± 0.0025 | 0.08316 ± 0.0025 |  |
| Laumanns | 100 | 100,100 | 16.64 ± 0.00076 | 0.01667 ± 4.8e-05 | 0.001869 ± 0.00011 | 0.007865 ± 0.001 |  |
| Murata | 100 | 100,100 | 3.895 ± 0.00041 | 0.009544 ± 5.1e-05 | 0.001605 ± 0.00051 | 0.005566 ± 0.00047 |  |
| Quagliarella | 100 | 100,100 | 9.097 ± 0.048 | 0.1038 ± 0.01 | 0.01243 ± 0.0011 | 0.008614 ± 0.0009 | front extremes need all 16 variables at 0 or 1.5 |
| Rendon | 100 | 100,100 | 38.93 ± 0.017 | 0.09526 ± 0.0026 | 0.01921 ± 0.0017 | 0.06122 ± 0.0036 |  |
| Rendon2 | 100 | 100,100 | 23.54 ± 0.0023 | 0.02578 ± 0.00022 | 0.003869 ± 0.00056 | 0.01604 ± 0.0012 |  |
| Schaffer | 100 | 100,100 | 16.63 ± 0.0012 | 0.01702 ± 0.00012 | 0.001935 ± 4.3e-05 | 0.00942 ± 0.00056 |  |
| Schaffer2 | 100 | 100,100 | 25.98 ± 0.0017 | 0.02273 ± 0.00063 | 0.003629 ± 0.00015 | 0.01364 ± 0.00076 |  |
| Srinivas | 100 | 100,100 | 3.493e+04 ± 4.3 | 0.8656 ± 0.014 | 0.3115 ± 0.062 | 0.536 ± 0.014 |  |
| Tanaka | 100 | 100,100 | 0.5132 ± 0.00017 | 0.003443 ± 9.7e-05 | 0.001014 ± 0.00016 | 0.002508 ± 0.00034 |  |
| Viennet | 100 | 100,100 | 32.43 ± 0.03 | 0.1262 ± 0.0032 | 0.1385 ± 0.017 | 0.04142 ± 0.0036 |  |
| Viennet2 | 100 | 100,100 | 0.8391 ± 0.00039 | 0.01204 ± 0.00067 | 0.01868 ± 0.0016 | 0.005987 ± 0.00058 |  |

## Observations

* **Converged very well** (IGD about 0.002-0.03, tiny run-to-run variation): ZDT1-4,
  ZDT6, DTLZ1, DTLZ5, Deb, Deb2, Fonseca, Fonseca2, Laumanns, Murata, Rendon2,
  Schaffer, Schaffer2, Tanaka, Viennet2. ZDT4 and DTLZ4 also converge reliably at
  this budget (they did not at 250 generations), and DTLZ6 improves markedly.
* **DTLZ1 and DTLZ3:** IGD is stable (0.014 and 0.036) but GD and Spacing have
  a huge standard deviation because a single stray solution in one run lies far
  from the front (e.g. DTLZ1 GD is 3.09 in seed 4 and about 0.005 in the others).
  The stray points are visible in the figures. These two problems have many local
  fronts, so a median or a trimmed mean describes them better than the mean.
* **DTLZ6** is the least converged DTLZ (IGD 0.035 ± 0.012), as expected for its
  biased, degenerate front.
* **Quagliarella:** IGD 0.10; SPEA2 does not reach the extremes of the front
  (f1 = 0 and f2 = 0 require all 16 variables at exactly 0 or 1.5).
* **Binh3:** the true front is a single point and every run reached it
  (IGD = GD = 0). Its HV is only the 0.1 margin of the reference point, not a
  quality measure.
* **Srinivas** metrics are in the units of a front spanning f1 in [10, 225]
  (IGD 0.87 is about 0.4 % of its length), so its HV cannot be compared with other
  problems. **Kursawe's** reference front has only 41 points, so its IGD (0.154) is
  coarse. **Rendon** and **Viennet** (IGD about 0.1) are dominated by the sparse
  coverage of the extreme parts of their fronts.

## Corrections made during verification

Found while checking results against the true fronts; fixed and tested. Earlier
runs affected are kept in `results/data/legacy_pre_alignment/`.

| Problem | Error | Fix |
|---|---|---|
| Srinivas | first reference front covered only x1 = -2.5; the true Pareto set also lies on the constraint line and circle | front now spans f1 in [10, 225] |
| Deb2 | reference was the whole x2 = 0 curve (about 78 % dominated points) | non-dominated segments only |
| DTLZ5 / DTLZ6 | reference used angle 0.25 instead of 0.5 (f1 != f2) | corrected |

## Caveats

* The metrics are only comparable with another algorithm if it uses the same
  reference fronts, hypervolume reference point and metric definitions (and scores
  the same kind of final set).
* DTLZ1 and DTLZ7 use 12 variables for all seven DTLZ problems, as in the shared
  configuration. The original DTLZ paper uses 7 (DTLZ1) and 22 (DTLZ7) for 3 objectives.
* 5 runs per problem is a small sample; standard deviations are indicative only.
