# SPEA2 on the CEC 2022 single-objective suite

Algorithm settings are the **original ones of this project** (they are not aligned
with the NSGA-II comparison protocol used for the multi-objective suites):
population = archive = 100, SBX applied to every variable with probability 0.9
(`per_variable` scheme, eta 20), polynomial mutation 1/n (eta 20), SPEA2 run with a
single objective (Pareto dominance reduces to ranking by function value), untuned.

**Protocol (technical report):** 12 functions, D = 10 and 20, search range
[-100, 100]^D, **30 runs** per function and dimension with seeds from the official
`Rand_Seeds.txt` (`seed_ind` rule), MaxFES 200,000 (D = 10) / 1,000,000 (D = 20) with
every solution evaluated once, termination at error 1e-8 (never reached),
errors recorded at the 16 checkpoints `floor(D^(k/5-3) * MaxFES)` plus FEterm.

Files (`results/data/cec2022_official_protocol/`):

* `raw_metrics_all.csv` - 720 rows (function, dim, run, seed, final error, FEterm,
  runtime); `summary_metrics_all.csv` - best / worst / median / mean / std;
* `results_format/SPEA2_<f>_<D>.txt` - the 17 x 30 matrices in the competition format
  (16 checkpoint errors + FEterm per run);
* `complexity.csv`, `complexity_system.json` - algorithm complexity.

The experiment was run in two parts with identical code and settings: 23 of the 24
(function, dimension) groups first, then the last one (F12, D = 20) with `--resume`.
Before resuming, ten earlier runs were recomputed and reproduced bit-for-bit.
Logs: `results/logs/cec2022_part1.log`, `cec2022_part2.log`. Total effort: about
40 CPU-hours (3.1 h at D = 10, 36.5 h at D = 20).

## Final error F(x) - F* after MaxFES (30 runs)

### D = 10 (MaxFES 200,000)

| F | Function | Best | Worst | Median | Mean | Std |
|---:|---|---|---|---|---|---|
| 1 | Zakharov | 3.0601e-02 | 1.1422e+00 | 1.8273e-01 | 2.9512e-01 | 2.7761e-01 |
| 2 | Rosenbrock | 1.1907e-01 | 8.9161e+00 | 7.8697e+00 | 6.3315e+00 | 3.2070e+00 |
| 3 | Expanded Schaffer f6 | 7.5617e-04 | 9.1337e-02 | 2.4692e-03 | 7.6466e-03 | 1.6472e-02 |
| 4 | Rastrigin (step) | 5.9698e+00 | 1.6914e+01 | 1.1442e+01 | 1.1774e+01 | 3.2748e+00 |
| 5 | Levy | 4.5646e-05 | 1.6688e+00 | 1.7923e-01 | 3.9752e-01 | 4.3417e-01 |
| 6 | Hybrid 1 | 6.9678e+01 | 5.8261e+03 | 1.0631e+03 | 1.4533e+03 | 1.5356e+03 |
| 7 | Hybrid 2 | 9.5490e-03 | 2.0045e+01 | 1.0933e+00 | 8.9418e+00 | 9.8547e+00 |
| 8 | Hybrid 3 | 3.7464e-02 | 2.1027e+01 | 2.0103e+01 | 1.4645e+01 | 8.9365e+00 |
| 9 | Composition 1 | 2.2928e+02 | 2.2928e+02 | 2.2928e+02 | 2.2928e+02 | 5.2226e-06 |
| 10 | Composition 2 | 1.0021e+02 | 2.1341e+02 | 1.0036e+02 | 1.1518e+02 | 3.8478e+01 |
| 11 | Composition 3 | 2.2621e-02 | 1.5051e+02 | 4.6743e-02 | 4.5161e+01 | 7.0102e+01 |
| 12 | Composition 4 | 1.6270e+02 | 1.6887e+02 | 1.6524e+02 | 1.6562e+02 | 1.5420e+00 |

### D = 20 (MaxFES 1,000,000)

| F | Function | Best | Worst | Median | Mean | Std |
|---:|---|---|---|---|---|---|
| 1 | Zakharov | 2.3838e-01 | 3.6937e+00 | 1.3161e+00 | 1.5619e+00 | 8.4826e-01 |
| 2 | Rosenbrock | 5.0598e+00 | 6.9952e+01 | 4.9085e+01 | 4.7341e+01 | 1.2518e+01 |
| 3 | Expanded Schaffer f6 | 2.0476e-04 | 1.3192e-02 | 1.8465e-03 | 2.4943e-03 | 2.4364e-03 |
| 4 | Rastrigin (step) | 1.9899e+01 | 5.6713e+01 | 3.7311e+01 | 3.6204e+01 | 9.7210e+00 |
| 5 | Levy | 1.5541e-04 | 3.1732e+01 | 4.3537e+00 | 7.0122e+00 | 7.8920e+00 |
| 6 | Hybrid 1 | 6.8852e+01 | 1.8491e+04 | 2.6293e+03 | 4.5601e+03 | 4.9148e+03 |
| 7 | Hybrid 2 | 2.2573e+01 | 8.1912e+01 | 4.0432e+01 | 4.4004e+01 | 1.8283e+01 |
| 8 | Hybrid 3 | 2.0472e+01 | 3.8232e+01 | 2.0919e+01 | 2.3151e+01 | 5.9288e+00 |
| 9 | Composition 1 | 1.8078e+02 | 1.8078e+02 | 1.8078e+02 | 1.8078e+02 | 3.2173e-04 |
| 10 | Composition 2 | 5.4282e-05 | 2.4389e+02 | 1.0042e+02 | 8.0024e+01 | 6.6208e+01 |
| 11 | Composition 3 | 3.0004e+02 | 4.0001e+02 | 3.0006e+02 | 3.0340e+02 | 1.8246e+01 |
| 12 | Composition 4 | 2.3435e+02 | 2.6763e+02 | 2.5075e+02 | 2.5195e+02 | 9.1866e+00 |

No run reached the 1e-8 target, so FEterm equals MaxFES in all 720 runs.

## Algorithm complexity (report section 2.2, item 4)

T0: 200,000 iterations of the reference loop; T1: 200,000 evaluations of F1; T2: mean
of 5 complete SPEA2 runs of 200,000 evaluations of F1 (population 100, archive 100).

| D | T0 (s) | T1 (s) | T2 (s) | (T2 − T1) / T0 |
|---:|---:|---:|---:|---:|
| 10 | 0.030 | 1.519 | 4.260 | 90.4 |
| 20 | 0.030 | 4.107 | 7.384 | 108.1 |

System: macOS (arm64, Apple silicon), Python 3.9, single-threaded, one solution
evaluated at a time, machine otherwise idle (see `complexity_system.json`). The
loop in T0 follows MATLAB semantics for `log(0) = -Inf`.

## Observations

* **Closest to the optimum:** F3 (mean error 0.0076 at D = 10, 0.0025 at D = 20) and
  F5 (0.40 and 7.0, with best runs around 1e-4), then F1 (0.30 and 1.6).
* **Unimodal-like and basic functions** F2 and F4 end at errors of about 6-12 (D = 10)
  and 36-47 (D = 20).
* **Hybrid functions:** F6 has by far the largest and most variable errors
  (mean 1,453 and 4,560, std larger than the mean), presumably because of its
  badly conditioned Bent-Cigar component (condition number 1e6); F7 and F8 are much smaller (9-44 and 15-23).
* **Composition functions:** F9 always ends at the same value (229.28 at D = 10 and
  180.8 at D = 20, std about 1e-5 to 3e-4), a local optimum; F10 varies strongly between
  runs (best about 1e-4, mean 80-115); F11 and F12 sit at about 300 / 250 (D = 20) and 45 / 166 (D = 10).
* SPEA2 is a multi-objective algorithm run here with a single objective and without
  tuning, so these numbers describe a baseline, not a competitive scalar optimiser.

## Notes on the benchmark implementation

`src/benchmarks/cec2022.py` is a port of the organisers' C reference, including its
quirks (F3 ignores the rotation, F4's step has no effect, Levy uses `sin(pi*w + 1)`,
the Schaffer F7 component of F7 reads its input from index 0); every function equals
its published optimum at the shifted optimum. The scoring of the report (Wilcoxon-based
ranking of several algorithms' trials) needs other algorithms' results and is not
computed.
