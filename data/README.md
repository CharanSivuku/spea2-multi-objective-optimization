# Benchmark data

Input data of the two CEC benchmark suites. Nothing here is produced by this
project's experiments; the files are the organisers' data (kept byte-for-byte for
CEC2022) or a lossless conversion of it (CEC2020 MMO).

## `cec2022/` - CEC 2022 single-objective suite (43 files, ~0.85 MB)

* **Source:** the competition organisers' repository
  <https://github.com/P-N-Suganthan/2022-SO-BO>, archive `CEC2022.zip`
  (SHA-256 `dd46b9efcfe79253c1dc0cb0f09c7f0ed0e24d5eb235ee14ca09be29f7def626`),
  folder `CEC2022/MATLAB/MATLAB/input_data/`.
* **Files copied** (dimensions 10 and 20 only): `M_<f>_D<dim>.txt` rotation
  matrices (f = 1..12), `shift_data_<f>.txt` shift vectors, `shuffle_data_<f>_D<dim>.txt`
  (f = 6, 7, 8) and `Rand_Seeds.txt` (1000 seeds).
* **Integrity:** `SHA256SUMS.txt` lists the checksum of every copied file; a test
  (`tests/test_cec2022.py`) verifies them.
* The organisers' Python archive (`Python-CEC2022.zip`) has the same data except
  `shift_data_8.txt`, which is shortened to one row there; the first row (the only
  one used for function 8) is identical. The Python code in that archive was
  read but **not used**: it is not functional (see `src/benchmarks/cec2022.py`).

## `cec2020_mmo/` - CEC 2020 multimodal multi-objective suite (48 files, ~1.7 MB)

* **Source:** the organisers' archive "CEC2020 MMO test problems", folder
  `MM_testfunctions/Reference_PSPF_data/` (`<name>_Reference_PSPF_data.mat`,
  MATLAB v5 files).
* **Conversion:** each `.mat` file holds the reference Pareto set `PS` and Pareto
  front `PF`. They were converted once to `<name>_PS.csv` and `<name>_PF.csv`
  (comma separated, 17 significant digits) with SciPy's `loadmat`, so the project
  needs no SciPy at run time.
* The per-problem settings (bounds, hypervolume reference point, number of Pareto
  sets) come from the organisers' `main.m`; see `src/benchmarks/cec2020_mmo.py`.
