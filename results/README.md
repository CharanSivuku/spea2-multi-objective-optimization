# Results

Final numbers behind the project report (settings shared with the NSGA-II baseline).

```
results/
├── all_benchmarks_summary.csv         30 standard benchmarks: mean/std of HV, IGD, GD, spacing
├── comparison/                        per-run results, reference fronts, obtained fronts (seed 1),
│                                      HV reference points (see comparison/README.md)
├── data/
│   ├── standard_suite_team_protocol/  raw_metrics_all.csv, summary_metrics_all.csv (30 problems, seeds 1-5)
│   ├── cec2020_mmo_team_protocol/     24 MMO problems, seeds 1-3
│   └── cec2022_official_protocol/     12 functions x D 10/20, 30 runs, complexity.csv
└── reports/                           written summaries of the three experiment groups
```

Figures and run logs are not included; regenerate them with the scripts in `experiments/`.
