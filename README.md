# SPEA2 Multi-Objective Optimization

Implementation of the Strength Pareto Evolutionary Algorithm 2 (SPEA2) from scratch in Python.

## Project Objective

The objective of this project is to implement and experimentally evaluate a multi-objective evolutionary algorithm.

SPEA2 is implemented from scratch without relying on an optimization library for the core algorithm.

The implementation will later be compared with other multi-objective evolutionary algorithms such as NSGA-II.

## Current Progress

- Pareto dominance
- Strength calculation
- Raw fitness
- Density estimation
- Final fitness assignment
- Environmental selection
- Archive truncation
- Tournament selection
- Simulated Binary Crossover
- Polynomial mutation
- ZDT1 benchmark function
- Population initialization
- SPEA2 evolutionary loop
- ZDT1 Pareto-front validation

## Repository Structure

```text
spea2-multi-objective-optimization/
│
├── src/
│   ├── __init__.py
│   └── spea2.py
│
├── experiments/
│   └── zdt1_experiment.py
│
├── results/
│   └── figures/
│       └── spea2_zdt1.png
│
├── tests/
│
├── README.md
├── requirements.txt
└── .gitignore