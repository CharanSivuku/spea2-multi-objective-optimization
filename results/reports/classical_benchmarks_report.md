# SPEA2 on the 12 newly added classical benchmarks

Configuration: population 100, archive 100, **250 generations**, 10 independent
runs, seeds 1–10, SBX/polynomial mutation settings unchanged. Note that the ZDT
results in the combined table use 500 generations (runner) or 250 generations
(legacy script), and DTLZ1/3/6 use 2000, so compare only rows with equal
generations. Metrics: HV, IGD, GD, Spacing (existing implementations).
Constrained problems (Srinivas, Tanaka) use feasibility-first constraint dominance;
only feasible archive members are scored (all 100 archive members were feasible in
every run).

Data: `results/data/05_classical12_new_250gen/{raw,summary}_metrics_all.csv`,
figures in `results/figures/`. Combined table:
`results/all_benchmarks_summary.csv`.

## Results (mean ± std over 10 runs)

| Benchmark | HV | IGD | GD | Spacing |
|---|---|---|---|---|
| Binh3 | 0.001 ± 0 | 0 ± 0 | 0 ± 0 | 0 ± 0 |
| Laumanns | 16.63 ± 0.0010 | 0.01682 ± 7.2e-5 | 0.002106 ± 4.9e-4 | 0.008305 ± 7.0e-4 |
| Murata | 3.894 ± 0.0005 | 0.00966 ± 1.1e-4 | 0.002605 ± 2.2e-3 | 0.005859 ± 4.6e-4 |
| Quagliarella | 8.767 ± 0.086 | 0.1727 ± 0.0198 | 0.01144 ± 0.0012 | 0.008255 ± 0.0010 |
| Rendon | 38.94 ± 0.018 | 0.09268 ± 0.0026 | 0.01982 ± 0.0014 | 0.05633 ± 0.0068 |
| Rendon2 | 23.54 ± 0.0018 | 0.02553 ± 4.6e-4 | 0.003737 ± 3.2e-4 | 0.01489 ± 0.0011 |
| Schaffer | 16.63 ± 0.0012 | 0.01702 ± 1.1e-4 | 0.001823 ± 1.1e-4 | 0.00939 ± 5.8e-4 |
| Schaffer2 | 25.98 ± 0.0018 | 0.02279 ± 5.4e-4 | 0.00362 ± 1.1e-4 | 0.01298 ± 0.0016 |
| Srinivas | 3.492e4 ± 8.7 | 0.8674 ± 0.016 | 0.3102 ± 0.056 | 0.5198 ± 0.072 |
| Tanaka | 0.5122 ± 3.2e-4 | 0.004212 ± 3.2e-4 | 0.002047 ± 1.4e-4 | 0.003013 ± 5.1e-4 |
| Viennet | 32.42 ± 0.035 | 0.1282 ± 0.0045 | 0.1382 ± 0.019 | 0.0393 ± 0.0037 |
| Viennet2 | 0.8389 ± 4.1e-4 | 0.01226 ± 7.1e-4 | 0.01793 ± 0.0017 | 0.005969 ± 5.1e-4 |

## Observations

* **Converged well:** Laumanns, Murata, Rendon2, Schaffer, Schaffer2, Tanaka,
  Viennet2 (IGD ≈ 0.004–0.026, tiny run-to-run variance). The plots overlap the
  reference fronts, including the disconnected fronts of Schaffer2 and Tanaka.
* **Binh3:** the true front is the single ideal point (x1 = x2 = 1e-6). All ten runs
  reached it (IGD = GD = 0). HV = 0.001 is just the product of the 0.1 margins of the
  shared reference-point rule, so it carries no information about quality.
* **Quagliarella:** the hardest problem. SPEA2 covers only the middle of the
  front (f1 ≈ 1.1–4.6); the extremes (f1 = 0 at x = 0, f2 = 0 at x = 1.5) need all
  16 Rastrigin variables at exactly 0 or 1.5 and are not reached in 250 generations.
  This is why IGD (0.17) is much larger than GD (0.011). The PDF reference stops at
  f1 ≈ 0.95, i.e. it appears to reflect what an algorithm finds, not the true front.
* **Srinivas:** metrics are in the units of a front spanning f1 ∈ [10, 225] and
  f2 ∈ [−218, 3], so IGD 0.87 is about 0.4 % of the front length. Its HV is large for
  the same reason and is not comparable with other problems.
* **Rendon, Viennet:** IGD 0.09–0.13 is dominated by sparse coverage of the
  extremes (Rendon's steep branch, Viennet's 2-D surface).
* Archives are padded with dominated solutions when fewer than 100 are
  non-dominated (existing SPEA2 behaviour, unchanged). This inflates GD and Spacing on
  3-objective problems (Viennet).

## Verification and caveats

* Formulas follow the MOEA Framework `problem.misc` sources and match every value
  range in `Benchmark_Comparison.pdf`, except where noted below.
* Reference fronts: analytical for Binh3, Laumanns, Murata, Rendon, Rendon2, Schaffer,
  Schaffer2, Viennet. Numerical but not randomly sampled: Srinivas, Tanaka
  (constraint-boundary parametrisation + ND filter), Quagliarella (exact
  dynamic-programming Minkowski sum, tested to ~0.004 accuracy), Viennet2 (weighted-sum
  minimisers of convex quadratics).
* **Correction made during this work:** my first Srinivas reference front, derived
  analytically as x1 = −2.5 only, was incomplete (the true Pareto set also lies on the
  g2 line and the g1 circle). It was found because SPEA2 reached feasible
  non-dominated points beyond it. It was replaced, a brute-force-grid test was added,
  and Srinivas was rerun. The earlier run is kept in
  `results/data/superseded_wrong_reference/Srinivas/`.
* Schaffer uses bounds [−10, 10] (literature uses 10 … 1e5); this affects search
  difficulty but not the front.
* Tanaka lower bound is 0 (literature: strictly positive); atan2 handles x2 = 0.
* Constraint dominance is opt-in; with `constraint_function=None` SPEA2 is
  bit-identical to before (tested).

## Status of the 30-benchmark goal

`results/all_benchmarks_summary.csv` now has metrics for all 30 benchmarks:

| Group | Runs | Source |
|---|---|---|
| ZDT1/2/3/4/6 | 10 | `results/data/01_zdt_500gen/` |
| DTLZ1/3/6 | **5** | `results/data/02_dtlz1-3-6_2000gen/` |
| DTLZ2/4/5/7, Binh1, Deb, Deb2, Fonseca, Fonseca2, Kursawe | 10 | `results/data/03_dtlz2-4-5-7_and_classical6_250gen/` |
| The 12 benchmarks above | 10 | `results/data/05_classical12_new_250gen/` |

### Errors found in pre-existing reference fronts (fixed, tested)

1. **Deb2:** the reference was the whole x2 = 0 curve, ~78 % of it dominated. Now
   only the non-dominated segments are used. IGD changed 0.185 -> 0.0045.
2. **DTLZ5/DTLZ6:** the reference used angle 0.25 instead of 0.5, so it was not on the
   true Pareto curve (f1 = f2). DTLZ5 IGD changed 0.245 -> 0.0045 after the fix.
   The first (wrong-reference) DTLZ5 and Deb2 runs are kept in
   `results/data/superseded_wrong_reference/`.

### Still open

* **DTLZ6:** the old 2000-generation result (set 02) was scored against a wrong
  reference front and is not trusted. A rerun with the corrected reference at 250
  generations (set 04) did not converge (HV 0, IGD about 1.39), so DTLZ6 still has no
  reliable result. It needs a longer run (e.g. 2000 generations) to be meaningful.
* DTLZ1/3/6 have 5 runs, not 10.
* Kursawe's reference front has only 41 points (sampled), so its IGD is coarse.
* ZDT3's reference contains ~4 dominated points out of 1000 (negligible).
