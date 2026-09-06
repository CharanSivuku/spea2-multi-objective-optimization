# SPEA2 Multi-Objective Optimization

Implementation and experimental evaluation of the Strength Pareto Evolutionary Algorithm 2 (SPEA2) on standard ZDT multi-objective optimization benchmarks.

## Project Objective

The objective of this project is to implement SPEA2 from scratch in Python and evaluate its performance on standard multi-objective optimization problems.

The core SPEA2 algorithm is implemented without relying on an external optimization library.

## Benchmarks

The implementation is evaluated on:

- ZDT1
- ZDT2
- ZDT3
- ZDT4
- ZDT6

All problems use two objectives and are treated as minimization problems.

## Experimental Protocol

The benchmark experiments use:

| Parameter | Value |
|---|---:|
| Population size | 100 |
| Archive size | 100 |
| Generations | 250 |
| Independent runs | 10 |
| Seeds | 1–10 |
| Crossover probability | 0.9 |
| SBX distribution index | 20 |
| Mutation probability | 1 / number of variables |
| Polynomial mutation index | 20 |
| Total evaluations/run | 25,100 |

The total number of function evaluations is:

```text
100 + 250 × 100 = 25,100