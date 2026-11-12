# SPEA2 on the CEC 2020 multimodal multi-objective (MMO) suite

**Protocol (shared with the NSGA-II baseline):** 24 problems, **3 independent runs
(seeds 1-3)**, population = archive = 100, 200 generations (= 201 iterations:
100 + 200 x 100 = **20,100 evaluations**), every new solution evaluated once.
The obtained sets are the non-dominated members of the final archive. Indicators
(all smaller-is-better): 1/PSP, 1/HV, IGDX (decision space) and IGDF (objective
space). SPEA2 is this project's real-coded SPEA2 (SBX 0.9 / eta 20, polynomial
mutation 1/n / eta 20), without niching in decision space.

This is *not* the official CEC 2020 protocol (21 runs, population 200 x N_ops,
MaxFES 10000 x N_ops); it is available in the runner (`--protocol official`) but
was not run for the final results.

Data: `results/data/cec2020_mmo_team_protocol/{raw,summary}_metrics_all.csv`
(one row per run with seed, all four indicators, CR, PSP, HV, runtime); figures:
`results/figures/mmf*.png` (obtained vs reference set and front, median-1/PSP run).
Runner: `experiments/run_cec2020_mmo.py`.

## Results (mean ± std over 3 runs)

| Problem | N_ops | 1/PSP ↓ | 1/HV ↓ | IGDX ↓ | IGDF ↓ |
|---|---:|---|---|---|---|
| MMF1 | 2 | 0.1078 ± 0.0097 | 1.147 ± 0.00017 | 0.1039 ± 0.007 | 0.003876 ± 4.9e-05 |
| MMF2 | 2 | 0.1223 ± 0.072 | 1.183 ± 0.045 | 0.1049 ± 0.043 | 0.03353 ± 0.044 |
| MMF4 | 2 | 0.1611 ± 0.02 | 1.859 ± 0.0002 | 0.1605 ± 0.02 | 0.004084 ± 0.00032 |
| MMF5 | 2 | 0.1658 ± 0.016 | 1.148 ± 6e-05 | 0.1636 ± 0.018 | 0.003998 ± 6.1e-05 |
| MMF7 | 2 | 0.06029 ± 0.016 | 1.148 ± 8e-05 | 0.05969 ± 0.016 | 0.004056 ± 5.7e-05 |
| MMF8 | 2 | 1.102 ± 0.61 | 2.381 ± 0.00014 | 0.8515 ± 0.4 | 0.004108 ± 2.2e-05 |
| MMF10 | 1 | 0.1302 ± 0.21 | 0.08059 ± 0.0049 | 0.1302 ± 0.21 | 0.1124 ± 0.16 |
| MMF11 | 1 | 0.009509 ± 0.00081 | 0.06899 ± 1.2e-05 | 0.009509 ± 0.00081 | 0.02454 ± 0.0016 |
| MMF12 | 1 | 0.002152 ± 9.2e-05 | 0.6357 ± 1.5e-05 | 0.002152 ± 9.2e-05 | 0.004145 ± 0.00011 |
| MMF13 | 1 | 0.2716 ± 0.19 | 0.05435 ± 2e-05 | 0.1348 ± 0.051 | 0.03348 ± 0.0018 |
| MMF14 | 2 | 0.1789 ± 0.095 | 0.1693 ± 0.00066 | 0.1783 ± 0.095 | 0.109 ± 0.005 |
| MMF15 | 1 | 0.05473 ± 0.0014 | 0.09318 ± 0.00022 | 0.05473 ± 0.0014 | 0.1062 ± 0.0011 |
| MMF1_e | 2 | 5.492 ± 3.3 | 1.149 ± 0.00075 | 2.261 ± 0.71 | 0.004309 ± 0.00017 |
| MMF14_a | 2 | 0.1277 ± 0.0079 | 0.1704 ± 0.00053 | 0.1257 ± 0.0048 | 0.1148 ± 0.0071 |
| MMF15_a | 1 | 0.07219 ± 0.0056 | 0.09411 ± 0.00018 | 0.07212 ± 0.0055 | 0.1209 ± 0.0027 |
| MMF10_l | 2 | 10.03 ± 8.2 | 0.08059 ± 0.0049 | 0.2013 ± 0.0046 | 0.1889 ± 0.019 |
| MMF11_l | 2 | 1.639 ± 0.42 | 0.06899 ± 1.2e-05 | 0.2532 ± 0.0013 | 0.1021 ± 0.00088 |
| MMF12_l | 2 | 4.824 ± 4.7 | 0.6357 ± 1.5e-05 | 0.247 ± 0.00085 | 0.08391 ± 4.3e-05 |
| MMF13_l | 2 | 1.431 ± 0.65 | 0.05435 ± 2e-05 | 0.3501 ± 0.042 | 0.1588 ± 0.00095 |
| MMF15_l | 2 | 0.5085 ± 0.078 | 0.09318 ± 0.00022 | 0.2737 ± 0.0011 | 0.21 ± 0.0058 |
| MMF15_a_l | 2 | 0.2758 ± 0.015 | 0.09411 ± 0.00018 | 0.2224 ± 0.0088 | 0.2017 ± 0.0029 |
| MMF16_l1 | 3 | 0.2749 ± 0.0038 | 0.0921 ± 0.00035 | 0.2126 ± 0.00079 | 0.1842 ± 0.00012 |
| MMF16_l2 | 3 | 0.5514 ± 0.22 | 0.09219 ± 0.00035 | 0.3247 ± 0.029 | 0.2545 ± 0.0077 |
| MMF16_l3 | 4 | 0.3748 ± 0.04 | 0.09229 ± 0.00024 | 0.2665 ± 0.027 | 0.2175 ± 0.0035 |

## Observations

* **Problems with only global Pareto sets** (MMF1, 2, 4, 5, 7, 8, 10-13, 14, 15 and the
  `_a` variants) are solved well in objective space (IGDF about 0.004-0.12) and
  reasonably in decision space (IGDX 0.002-0.2; MMF8 0.85 and MMF1_e 2.3 are the
  hard ones). With a population of only 100 the decision-space coverage is coarser
  than with the official population (200 x N_ops).
* **Problems with local Pareto sets** (`_l`, MMF16_*) are much harder in decision
  space (IGDX 0.2-0.35): the local sets map to dominated fronts, which a
  Pareto-based algorithm discards.
* **MMF1_e** has a wide search range (x2 in [-20, 20]); IGDX is 2.3 although IGDF
  is small.
* 1/PSP is close to IGDX when the cover rate is about 1 (PSP = CR / IGDX).

## Issues in the organisers' data and settings (replicated, not "fixed")

* **MMF13_l:** its reference PS has x3 up to 1.32 but the declared bounds are
  [0.1, 1.1], so part of the reference set cannot be reached.
* **MMF12_l and MMF13_l:** the hypervolume reference points from `main.m` do not
  cover their local reference fronts, so those front parts add nothing to HV.
* **MMF2:** the official code subtracts 1 from x2 only when x2 > 1, so the reference
  point (0, 1) on the boundary maps off the front.
* **Hypervolume:** the organisers' MATLAB code is valid for two objectives only; this
  project uses its exact N-dimensional hypervolume.
* The reference PF of MMF5 and MMF8 is a coarse sample.
* CR ignores one variable for MMF10/11/12 (variable 2) and MMF14/15 (variable 3), as
  in the MATLAB code, and not for the `_l` variants.

## Caveats

Only 3 runs, so standard deviations are rough. The numbers describe a baseline: SPEA2
has no mechanism to keep several Pareto sets that share a front.
