## 1. Population Initialization

A population of candidate solutions is randomly generated within the specified variable bounds.

For most ZDT problems:

```
```

```
x_i ∈ [0, 1]
```

For ZDT4, mixed bounds are used:

```
```

```
x_1 ∈ [0, 1]

x_2 ... x_n ∈ [-5, 5]
```

---

## 2. Strength Calculation

For every solution, the strength value represents the number of solutions it dominates.

```math
S(i) = |\{j \mid i \prec j\}|
```

A solution that dominates many other solutions receives a higher strength value.

---

## 3. Raw Fitness

Raw fitness is calculated using the strengths of the solutions that dominate the current solution.

```math
R(i) = \sum_{j \prec i} S(j)
```

Non-dominated solutions have a raw fitness of zero.

Lower fitness is preferred.

---

## 4. Density Estimation

SPEA2 also considers how crowded a solution's neighborhood is.

The implementation uses the distance to the `k`-th nearest neighbor:

```math
D(i) = \frac{1}{\sigma_k(i) + 2}
```

where:

```math
k = \max(1,\lfloor\sqrt{N}\rfloor)
```

and `N` is the size of the combined population and archive.

This encourages diversity by preferring solutions located in less crowded regions.

---

## 5. Final Fitness

The final fitness combines raw fitness and density:

```math
F(i) = R(i) + D(i)
```

Lower fitness is preferred.

The environmental selection step primarily keeps solutions satisfying:

```math
F(i) < 1
```

---

# Environmental Selection

Environmental selection operates on the combined population and archive.

The selection process is:

1.  Identify solutions with fitness `< 1`. 
2.  If there are too many such solutions, perform archive truncation. 
3.  If there are too few, fill the archive using the best remaining solutions according to fitness. 
4.  Produce the new archive. 

This maintains a fixed archive capacity of 100 solutions in the experiments.

---

# Archive Truncation

When more than the allowed number of non-dominated solutions are available, SPEA2 must remove solutions while preserving diversity.

The implementation compares nearest-neighbor distance information lexicographically.

The objective is to remove solutions from overly crowded regions while retaining a diverse approximation of the Pareto front.

---

# Parent Selection

Parents are selected using **binary tournament selection**.

Two candidate solutions are sampled and the one with better fitness is selected.

Since SPEA2 minimizes fitness:

```
```

```
lower fitness → better candidate
```

The process is repeated until enough parents are available to generate the next population.

---

# Simulated Binary Crossover (SBX)

The implementation uses **Simulated Binary Crossover (SBX)** for real-valued decision variables.

Parameters used in the experiments:

```
```

```
Crossover probability = 0.9
Distribution index ηc = 20
```

The generated offspring are clipped to the corresponding variable bounds.

---

# Polynomial Mutation

Polynomial mutation is applied independently to offspring variables.

The mutation probability is:

```math
P_m = \frac{1}{n}
```

where `n` is the number of decision variables.

The polynomial mutation distribution index is:

```
```

```
ηm = 20
```

Mutated values are also clipped to their valid bounds.

---

# Benchmark Problems

The implementation is evaluated on five standard ZDT benchmark functions.

## ZDT1

ZDT1 is a continuous bi-objective benchmark with a convex Pareto front.

It is commonly used to evaluate convergence and distribution of solutions on a smooth Pareto front.

---

## ZDT2

ZDT2 has a continuous but non-convex Pareto front.

It tests whether an algorithm can approximate a curved non-convex front.

---

## ZDT3

ZDT3 contains a **discontinuous Pareto front** consisting of several separate regions.

It therefore tests the ability of an optimization algorithm to maintain diversity across disconnected Pareto-optimal regions.

---

## ZDT4

ZDT4 contains many local optima in the decision space.

It is particularly useful for evaluating an algorithm's ability to avoid local optima and maintain convergence under a limited evaluation budget.

ZDT4 uses mixed decision-variable bounds:

```
```

```
x1 ∈ [0, 1]

x2 ... x30 ∈ [-5, 5]
```

---

## ZDT6

ZDT6 contains a non-uniform Pareto-optimal solution distribution.

It tests whether the algorithm can maintain a good approximation when the desired solution distribution is non-uniform.

---

# Experimental Protocol

The same experimental protocol is used for all five benchmarks.

| ParameterValue             |                         |
| -------------------------- | ----------------------- |
| Population size            | 100                     |
| Archive size               | 100                     |
| Generations                | 250                     |
| Independent runs           | 10                      |
| Seeds                      | 1–10                    |
| Objectives                 | 2                       |
| Crossover probability      | 0.9                     |
| SBX distribution index     | 20                      |
| Mutation probability       | 1 / number of variables |
| Polynomial mutation index  | 20                      |
| Function evaluations / run | 25,100                  |

The total number of function evaluations is:

```math
NFE = 100 + 250 \times 100
```

```math
NFE = 25,100
```

Each benchmark is executed independently using seeds:

```
```

```
1, 2, 3, ..., 10
```

This provides multiple independent observations rather than relying on a single stochastic run.

---

# Evaluation Metrics

Four performance indicators are used.

## Hypervolume (HV)

Hypervolume measures the volume of objective space dominated by the obtained Pareto front with respect to a reference point.

For the experiments, the reference point is:

```
```

```
[1.1, 1.1]
```

For minimization:

```
```

```
Higher HV → better
```

---

## Inverted Generational Distance (IGD)

IGD measures how far the obtained approximation is from a reference Pareto front.

It evaluates both convergence and coverage of the obtained solutions.

```
```

```
Lower IGD → better
```

---

## Generational Distance (GD)

GD measures the distance from the obtained solutions to the reference Pareto front.

It primarily evaluates convergence.

```
```

```
Lower GD → better
```

---

## Spacing

Spacing evaluates the distribution and uniformity of solutions along the obtained front.

A smaller spacing value indicates a more uniform distribution.

```
```

```
Lower Spacing → better
```

---

# Results

The following values are the mean ± standard deviation over 10 independent runs.

| BenchmarkHV ↑IGD ↓GD ↓Spacing ↓ |                       |                     |                     |                     |
| ------------------------------- | --------------------- | ------------------- | ------------------- | ------------------- |
| ZDT1                            | 0.868337 ± 0.000633   | 0.004843 ± 0.000267 | 0.002902 ± 0.000373 | 0.002299 ± 0.000146 |
| ZDT2                            | 0.535224 ± 0.000355   | 0.004603 ± 0.000135 | 0.002260 ± 0.000244 | 0.002328 ± 0.000304 |
| ZDT3                            | 1.315779 ± 0.025962\* | 0.010841 ± 0.017632 | 0.002144 ± 0.000329 | 0.003464 ± 0.000393 |
| ZDT4                            | 0.000000 ± 0.000000   | 4.241244 ± 1.832326 | 5.112376 ± 2.231289 | 0.592988 ± 1.158240 |
| ZDT6                            | 0.491774 ± 0.001206   | 0.009988 ± 0.000822 | 0.009618 ± 0.000945 | 0.001935 ± 0.000209 |

**Metric direction:**

-  ↑ Higher is better 
-  ↓ Lower is better 

### ZDT3 HV Note

The ZDT3 hypervolume value is retained from the current implementation and experimental output.

However, the HV definition/reference policy has not been reconciled with the PESA-II baseline used for comparison. Therefore, the ZDT3 HV values should **not be interpreted as a direct apples-to-apples comparison** with the reported PESA-II HV until the metric/reference definitions are aligned.

---

# Experimental Data

The project stores both individual-run and aggregated experimental results.

## Raw Metrics

```
```

```
results/raw_metrics.csv
```

This file contains the result of every benchmark/seed combination.

Format:

```
```

```
benchmark,seed,hv,igd,gd,spacing,archive_size,nfe,runtime_seconds
```

There are 10 runs for each benchmark.

---

## Summary Metrics

```
```

```
results/summary_metrics.csv
```

This file contains aggregated statistics for every benchmark, including:

-  mean 
-  standard deviation 
-  median 
-  minimum 
-  maximum 

for:

-  Hypervolume 
-  IGD 
-  GD 
-  Spacing 
-  Archive size 
-  Number of function evaluations 
-  Runtime 

---

# Comparison with PESA-II

The experimental protocol follows the protocol reported for the PESA-II baseline:

| ParameterValue        |        |
| --------------------- | ------ |
| Population            | 100    |
| Archive               | 100    |
| Generations           | 250    |
| Independent runs      | 10     |
| Seeds                 | 1–10   |
| NFE/run               | 25,100 |
| Crossover probability | 0.9    |
| SBX index             | 20     |
| Mutation probability  | 1/n    |
| Mutation index        | 20     |

The comparison is based on:

-  HV 
-  IGD 
-  GD 
-  Spacing 

## PESA-II Baseline

| BenchmarkHV ↑IGD ↓GD ↓Spacing ↓ |                 |                 |                 |                 |
| ------------------------------- | --------------- | --------------- | --------------- | --------------- |
| ZDT1                            | 0.8605 ± 0.0023 | 0.0103 ± 0.0017 | 0.0015 ± 0.0003 | 0.0084 ± 0.0009 |
| ZDT2                            | 0.5232 ± 0.0033 | 0.0110 ± 0.0012 | 0.0015 ± 0.0004 | 0.0078 ± 0.0011 |
| ZDT3                            | 0.7167 ± 0.0091 | 0.0161 ± 0.0212 | 0.0006 ± 0.0002 | 0.0065 ± 0.0008 |
| ZDT4                            | 0.8445 ± 0.0139 | 0.0262 ± 0.0203 | 0.2838 ± 0.4165 | 0.8271 ± 1.2527 |
| ZDT6                            | 0.5908 ± 0.0262 | 0.0522 ± 0.0155 | 1.2607 ± 0.2148 | 0.3295 ± 0.3700 |

---

# Comparison Summary

## ZDT1

SPEA2 achieves:

-  higher HV 
-  lower IGD 
-  lower Spacing 

The reported PESA-II baseline has lower GD.

Overall, SPEA2 shows strong convergence and distribution performance on ZDT1, although GD favors PESA-II.

---

## ZDT2

SPEA2 achieves:

-  higher HV 
-  lower IGD 
-  lower Spacing 

PESA-II reports lower GD.

This indicates that SPEA2 provides a strong overall approximation of the ZDT2 Pareto front while PESA-II has an advantage in the particular GD measure.

---

## ZDT3

SPEA2 achieves lower:

-  IGD 
-  Spacing 

The reported PESA-II baseline has lower GD.

The HV comparison is intentionally excluded because the reference/metric definitions have not been reconciled.

---

## ZDT4

ZDT4 is the most difficult benchmark for this implementation under the fixed 25,100-evaluation budget.

The obtained result is:

```
```

```
HV = 0.000000 ± 0.000000
IGD = 4.241244 ± 1.832326
GD = 5.112376 ± 2.231289
```

This indicates poor convergence within the fixed evaluation budget.

A separate longer diagnostic run showed that the implementation can move much closer to the ZDT4 Pareto region when given substantially more generations. Therefore, the observed result is strongly related to the difficulty of ZDT4 under the fixed experimental budget.

The PESA-II baseline performs substantially better on ZDT4 under the same reported budget.

---

## ZDT6

SPEA2 achieves substantially lower:

-  IGD 
-  GD 
-  Spacing 

while the reported PESA-II baseline has higher HV.

This shows that the algorithms can rank differently depending on which aspect of solution quality is measured.

---

# Important Observations

## 1. SPEA2 performs strongly on ZDT1 and ZDT2

The low IGD and GD values indicate good convergence toward the reference fronts.

The small standard deviations also indicate stable behavior across the 10 independent runs.

---

## 2. ZDT3 is more challenging

ZDT3 contains a discontinuous Pareto front.

The relatively larger IGD standard deviation is influenced by one weaker run, while most runs remain close to the other observed values.

The HV metric requires reference-policy reconciliation before direct comparison with the PESA-II result.

---

## 3. ZDT4 is the major difficulty

ZDT4 has many local optima and a large search space in variables `x2...xn`.

Under the fixed:

```
```

```
250 generations
100 population
25,100 evaluations
```

the implementation does not consistently reach the Pareto-optimal region.

This is reflected by:

```
```

```
HV = 0
High IGD
High GD
```

This result is retained rather than artificially modifying the experimental protocol to obtain a better value.

---

## 4. ZDT6 shows good convergence

The relatively low IGD and GD values indicate that the implementation reaches the reference front reasonably well.

The low spacing value also indicates a relatively uniform distribution of the obtained solutions.

---

## 5. Mean and Standard Deviation are Both Important

Because evolutionary algorithms are stochastic, one run is not sufficient to characterize performance.

Using 10 independent seeds provides a better estimate of typical behavior.

The reported format:

```
```

```
mean ± standard deviation
```

shows both average performance and run-to-run variability.

---

# Project Structure

```
```

```
Spea2_Project/
│
├── src/
│   ├── __init__.py
│   ├── spea2.py
│   │
│   └── metrics/
│       ├── __init__.py
│       ├── gd.py
│       ├── hypervolume.py
│       ├── igd.py
│       └── spacing.py
│
├── experiments/
│   ├── zdt_benchmarks.py
│   └── zdt1_experiment.py
│
├── results/
│   ├── raw_metrics.csv
│   ├── summary_metrics.csv
│   └── figures/
│       ├── zdt1/
│       ├── zdt2/
│       ├── zdt3/
│       ├── zdt4/
│       ├── zdt6/
│       └── spea2_zdt1.png
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Installation

Clone the repository:

```
```

```
git clone https://github.com/CharanSivuku/spea2-multi-objective-optimization.git
cd spea2-multi-objective-optimization
```

Create a virtual environment:

```
```

```
python3 -m venv .venv
```

Activate it.

### macOS / Linux

```
```

```
source .venv/bin/activate
```

### Windows

```
```

```
.venv\Scripts\activate
```

Install dependencies:

```
```

```
pip install -r requirements.txt
```

---

# Running the Experiments

Run the complete ZDT benchmark experiment:

```
```

```
PYTHONPATH=. python experiments/zdt_benchmarks.py
```

The experiment evaluates:

```
```

```
ZDT1
ZDT2
ZDT3
ZDT4
ZDT6
```

using seeds 1–10.

The script:

1.  Runs SPEA2 
2.  Records runtime 
3.  Calculates HV 
4.  Calculates IGD 
5.  Calculates GD 
6.  Calculates Spacing 
7.  Records archive size 
8.  Records NFE 
9.  Writes raw results 
10.  Calculates summary statistics 

Results are written to:

```
```

```
results/raw_metrics.csv
results/summary_metrics.csv
```

The terminal prints a compact summary:

```
```

```
========== ZDT1 ==========
HV:       0.868337 ± 0.000633
IGD:      0.004843 ± 0.000267
GD:       0.002902 ± 0.000373
Spacing:  0.002299 ± 0.000146

========== ZDT2 ==========
HV:       0.535224 ± 0.000355
IGD:      0.004603 ± 0.000135
GD:       0.002260 ± 0.000244
Spacing:  0.002328 ± 0.000304

========== ZDT3 ==========
HV:       1.315779 ± 0.025962
IGD:      0.010841 ± 0.017632
GD:       0.002144 ± 0.000329
Spacing:  0.003464 ± 0.000393

========== ZDT4 ==========
HV:       0.000000 ± 0.000000
IGD:      4.241244 ± 1.832326
GD:       5.112376 ± 2.231289
Spacing:  0.592988 ± 1.158240

========== ZDT6 ==========
HV:       0.491774 ± 0.001206
IGD:      0.009988 ± 0.000822
GD:       0.009618 ± 0.000945
Spacing:  0.001935 ± 0.000209
```

---

# Running the Tests

Run the test suite with:

```
```

```
PYTHONPATH=. pytest
```

The test suite provides regression coverage for the implemented SPEA2 components and benchmark functionality.

---

# Reproducibility

The experiments use deterministic random seeds:

```
```

```
1 through 10
```

For every benchmark, the same experimental settings are used.

This makes it possible to reproduce the reported results under the same software and execution environment.

The experimental configuration is:

```
```

```
Population = 100
Archive = 100
Generations = 250
Runs = 10
Seeds = 1–10
Crossover probability = 0.9
SBX eta = 20
Mutation probability = 1/n
Polynomial mutation eta = 20
NFE = 25,100/run
```

---

# Implementation Notes

## No External Optimization Framework

The core SPEA2 algorithm is implemented directly in Python.

The implementation does not rely on an external multi-objective optimization library for:

-  dominance 
-  fitness assignment 
-  environmental selection 
-  archive truncation 
-  parent selection 
-  crossover 
-  mutation 

This makes the implementation useful for understanding the internal mechanics of SPEA2.

---

## Generic Objective Function

The main `spea2()` implementation accepts an objective function rather than hard-coding a single benchmark.

This allows the same optimizer to be used with:

```
```

```
ZDT1
ZDT2
ZDT3
ZDT4
ZDT6
```

---

## Variable Bounds

The implementation supports both:

-  scalar bounds 
-  per-variable bounds 

This is required for benchmarks such as ZDT4, where the first variable and remaining variables have different ranges.

---

# Limitations

The current project has several known limitations.

### ZDT4 Convergence

ZDT4 remains difficult under the fixed 25,100-evaluation budget.

The current implementation therefore reports poor ZDT4 convergence rather than changing the experimental protocol.

### ZDT3 Hypervolume Comparison

The ZDT3 HV value is retained from the current implementation, but its direct comparison with the PESA-II HV value is deferred until the reference-point and metric definitions are reconciled.

### Computational Cost

The implementation is designed primarily for clarity and experimentation rather than highly optimized execution.

---

# Future Improvements

Possible extensions include:

-  Additional multi-objective benchmark functions 
-  More extensive statistical testing 
-  Improved Pareto-front visualization 
-  Convergence plots across generations 
-  Hypervolume progression plots 
-  Comparison with additional evolutionary algorithms 
-  Performance profiling and optimization 
-  Larger numbers of independent runs 
-  Automated experiment configuration 
-  Automated result reporting 

---

# Conclusion

This project provides a from-scratch implementation of SPEA2 and evaluates its behavior across several standard multi-objective optimization benchmarks.

The experiments demonstrate that the implementation performs strongly on smooth continuous problems such as **ZDT1 and ZDT2**, while more difficult problems such as **ZDT4** expose the challenges of convergence under a fixed evaluation budget.

The use of multiple metrics and independent runs provides a more complete evaluation than relying on a single performance indicator.

The project demonstrates the complete workflow of a multi-objective evolutionary optimization experiment:

```
```

```
Algorithm Implementation
        ↓
Benchmark Problems
        ↓
Independent Runs
        ↓
Performance Metrics
        ↓
Statistical Summary
        ↓
Baseline Comparison
        ↓
Experimental Analysis
```

The implementation, experiments, metrics, tests, and generated results are organized so that the experiments can be reproduced and extended.

---

## License

This project is intended for educational