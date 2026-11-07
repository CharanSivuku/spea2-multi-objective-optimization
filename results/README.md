# Results guide

Everything produced by the SPEA2 benchmark experiments, organised by purpose.

```
results/
├── README.md                      this file
├── all_benchmarks_summary.csv     one row per benchmark (30): runs, generations,
│                                  source set, note, and mean/std of HV, IGD, GD, Spacing
├── MANIFEST.tsv                   where every file came from before the reorganisation
│
├── figures/                       ALL figures live here (one PNG per benchmark)
│   ├── _overview_all_30.png       contact sheet of the 30 main benchmarks
│   ├── zdt1.png ... viennet2.png  30 current figures (lower-case benchmark name)
│   ├── mmf1.png ... mmf16_l3.png  24 CEC 2020 MMO figures (obtained vs reference set + front)
│   └── archive/                   older / superseded figures, kept for the record
│
├── data/                          raw + summary CSVs, one folder per run set
│   ├── 01_zdt_500gen/                         ZDT1/2/3/4/6        10 runs, 500 generations
│   ├── 02_dtlz1-3-6_2000gen/                  DTLZ1/3/6            5 runs, 2000 generations
│   ├── 03_dtlz2-4-5-7_and_classical6_250gen/  DTLZ2/4/5/7, Binh1, Deb, Deb2,
│   │                                          Fonseca, Fonseca2, Kursawe
│   │                                          10 runs, 250 generations
│   ├── 04_dtlz6_250gen_rerun/                 DTLZ6               10 runs, 250 generations
│   ├── 05_classical12_new_250gen/             Binh3, Laumanns, Murata, Quagliarella,
│   │                                          Rendon, Rendon2, Schaffer, Schaffer2,
│   │                                          Srinivas, Tanaka, Viennet, Viennet2
│   │                                          10 runs, 250 generations
│   ├── 06_cec2020_mmo_21runs/                 CEC 2020 MMO suite: 24 problems, 21 runs,
│   │                                          pop 200*N_ops, 50 generations (raw + summary)
│   └── superseded_wrong_reference/            runs scored against a wrong reference
│                                              front (Srinivas, DTLZ5, Deb2); not used
│
├── reports/
│   ├── classical_benchmarks_report.md         results, verification and caveats for the
│   │                                          12 newly added benchmarks
│   └── cec2020_mmo_report.md                  CEC 2020 MMO results and data issues
└── logs/                          console output of every run
```

Each `data/` folder holds `raw_metrics_all.csv` (one row per run, with seed) and
`summary_metrics_all.csv` (mean/std over runs). Folders 03 and 05 also contain
`per_benchmark/<Name>/` copies of the individual runs they were merged from.
Folder 01 additionally has the older `raw_metrics.csv` / `summary_metrics.csv`
written by `experiments/zdt_benchmarks.py`, plus `zdt1_metrics.txt`.

## Things to know

* **Generation budgets differ between sets** (500 / 2000 / 250). Compare values
  only within the same `generations` value in `all_benchmarks_summary.csv`.
* `data/01_zdt_500gen/raw_metrics.csv` and `summary_metrics.csv` are an older,
  separate ZDT experiment: 250 generations, ZDT4 with 30 variables, fixed HV
  reference [1.1, 1.1] (its NFE column uses `100 + G*100`, so 25,100 = 250
  generations). `raw_metrics_all.csv` in the same folder is the 500-generation
  runner set that feeds the combined table.
* **DTLZ6** at 250 generations did not converge (HV 0). Its 2000-generation run in
  set 02 was scored against a wrong reference front and is not trusted.
* Reference-front fixes made during this work: Deb2 (non-dominated only), DTLZ5/6
  (angle 0.5), Srinivas (full front). Affected old runs are in
  `data/superseded_wrong_reference/` and `figures/archive/`.
* `figures/archive/*_legacy_*` are older figures of unknown run budget, kept only
  because they could not be matched to a metrics file.
* Rebuild the combined table with `python experiments/merge_results.py`. It covers
  the 30 main benchmarks only; the CEC 2020 MMO results (set 06) have their own
  summary file, and the CEC 2022 suite has no results yet.
* The legacy script `experiments/zdt_benchmarks.py` still writes to
  `results/raw_metrics.csv` if re-run; use `experiments/run_benchmarks.py
  --output-dir ...` instead.
