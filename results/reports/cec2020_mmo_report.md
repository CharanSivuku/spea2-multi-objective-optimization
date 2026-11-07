# SPEA2 on the CEC 2020 multimodal multi-objective (MMO) suite

**Protocol** (technical report section 2.2 and the organisers' `main.m`): 24 problems,
**21 independent runs** (seeds 1-21), population = archive = 200 x N_ops,
MaxFES = 10000 x N_ops, i.e. **50 generations** with every new solution evaluated
once. The obtained sets are the non-dominated members of the final archive.
Indicators (all smaller-is-better): 1/PSP, 1/HV, IGDX (decision space) and IGDF
(objective space). The algorithm is this project's real-coded SPEA2 (SBX /
polynomial mutation, no niching in decision space), not the organisers' MATLAB
SPEA2.

Data: `results/data/06_cec2020_mmo_21runs/{raw,summary}_metrics_all.csv`
(one row per run with seed, all four indicators, CR, PSP, HV, runtime);
figures: `results/figures/mmf*.png` (obtained vs reference Pareto set and front,
median-1/PSP run). Runner: `experiments/run_cec2020_mmo.py`.

## Results (mean ± std over 21 runs)

| Problem | N_ops | 1/PSP ↓ | 1/HV ↓ | IGDX ↓ | IGDF ↓ |
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

Best / worst / median per indicator are in the summary CSV.

## Observations

* **Problems with only global Pareto sets** (MMF1, 2, 4, 5, 7, 8, 10-13, 14, 15 and
  the `_a` variants) are solved well in objective space (IGDF about 0.001-0.08) and
  mostly well in decision space (IGDX 0.0015-0.08; MMF8 0.28). In the MMF1 plot
  the run covers both Pareto-set branches although SPEA2 has no decision-space
  niching; with population 400 the random sampling plus crossover keeps both.
* **Problems with local Pareto sets** (`_l`, MMF16_*) are much harder in decision
  space: IGDX 0.15-0.32, because the local PS maps to a dominated front, so a
  Pareto-based algorithm discards it.
* **MMF1_e** has a wide search range (x2 in [-20, 20]) with an exponentially
  growing amplitude; IGDX is 1.65 even though IGDF is small.
* 1/PSP equals roughly IGDX when the cover rate is about 1 (PSP = CR / IGDX).

## Issues in the organisers' data and settings (replicated, not "fixed")

* **MMF13_l:** its reference PS has x3 up to 1.32 but the declared bounds are
  [0.1, 1.1], so part of the reference set cannot be reached.
* **MMF12_l and MMF13_l:** the hypervolume reference points from `main.m`
  ([1.54, 1.1] and [1.54, 15.4]) do not cover their local reference fronts
  (f2 up to 1.33 and 17.1), so those front parts add nothing to HV.
* **MMF2:** the official code subtracts 1 from x2 only when x2 > 1, so the
  reference point (0, 1) lying exactly on the boundary maps off the front.
* **Hypervolume:** the organisers' MATLAB `Hypervolume_calculation` sums 2-D boxes
  on the first two objectives and is only valid for two objectives, although the
  suite has 3-objective problems. This project uses its exact N-dimensional
  hypervolume instead.
* The reference PF of MMF5 and MMF8 is a coarse sample: the objective values of the
  reference PS lie on the analytic front but not exactly on the sampled points.
* CR ignores one variable for MMF10/11/12 (variable 2) and MMF14/15 (variable 3)
  as in the MATLAB code, and, as there, not for the `_l` variants.

## Caveats

The budget of 50 generations is the competition's, not tuned for SPEA2; the
algorithm has no mechanism to maintain several Pareto sets that share a front, so
the numbers describe a baseline, not a competitive MMO method.
