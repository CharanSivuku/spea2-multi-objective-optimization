"""CEC 2022 single-objective bound-constrained benchmark suite (12 functions).

This is a line-by-line Python port of the organisers' reference code
(`cec22_test_func.cpp`, MATLAB/C package of the CEC 2022 competition), using the
official shift, rotation and shuffle data in `data/cec2022/`.

Why a port of the C code and not of the PDF or the organisers' Python file:
the organisers' own Python file is not usable (it calls an undefined
`griewank_func`, keeps module-level state that is reset on every call, ...),
and the PDF omits implementation details. The C code defines the values the
competition results are based on, so this port reproduces it, *including its
quirks*, which are documented here rather than silently "fixed":

* F3 (called ``schaffer_F7_func`` in the C code) computes its pair distances
  from the shifted-and-scaled but **un-rotated** vector (the global ``y`` that
  ``sr_func`` fills before rotating), so the rotation matrix has no effect.
* ``step_rastrigin_func`` (F4) edits ``y`` before ``sr_func`` overwrites it, so
  the "non-continuous" step has no effect and F4 equals a rotated Rastrigin.
* ``levy_func`` (F5) uses ``sin(pi*w + 1)`` inside the sum, as in the C code.
* In Hybrid Function 2 (F7) the Schaffer F7 component reads the global ``y`` from
  index 0 instead of from the start of its own variable group.

Functions F1-F12, search range [-100, 100]^D, D in {10, 20}. All are
minimisation problems with known global optimum value ``F_STAR[f]`` at the
shifted optimum ``o``.

The composition functions need up to 6 shift vectors and 6 rotation matrices;
the data files ship 10 of each (the C code reads 12 but never uses more than 6).
"""

import math
from pathlib import Path
from typing import List, Sequence

import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "cec2022"

F_STAR = {
    1: 300.0, 2: 400.0, 3: 600.0, 4: 800.0, 5: 900.0, 6: 1800.0,
    7: 2000.0, 8: 2200.0, 9: 2300.0, 10: 2400.0, 11: 2600.0, 12: 2700.0,
}

FUNCTION_NAMES = {
    1: "Shifted and full Rotated Zakharov",
    2: "Shifted and full Rotated Rosenbrock",
    3: "Shifted and full Rotated Expanded Schaffer's f6 (rotation unused, see module doc)",
    4: "Shifted and full Rotated Non-Continuous Rastrigin (step unused, see module doc)",
    5: "Shifted and full Rotated Levy",
    6: "Hybrid Function 1 (N = 3)",
    7: "Hybrid Function 2 (N = 6)",
    8: "Hybrid Function 3 (N = 5)",
    9: "Composition Function 1 (N = 5)",
    10: "Composition Function 2 (N = 3)",
    11: "Composition Function 3 (N = 5)",
    12: "Composition Function 4 (N = 6)",
}

LOWER = -100.0
UPPER = 100.0
SUPPORTED_DIMENSIONS = (10, 20)

INF = 1.0e99
E = math.e
PI = math.pi


class _Data:
    """Official data for one (function, dimension) pair."""

    def __init__(self, func_num: int, dim: int):
        if func_num not in F_STAR:
            raise ValueError(f"CEC2022 has functions 1..12, got {func_num}")
        if dim not in SUPPORTED_DIMENSIONS:
            raise ValueError(f"Supported dimensions are {SUPPORTED_DIMENSIONS}")

        m = np.loadtxt(DATA_DIR / f"M_{func_num}_D{dim}.txt")
        shift = np.loadtxt(DATA_DIR / f"shift_data_{func_num}.txt")

        if func_num < 9:
            self.M = m.reshape(dim, dim)
            self.shift = shift.reshape(-1)[:dim].copy()
        else:
            # composition: one rotation matrix / shift vector per component
            self.M = m.reshape(-1, dim, dim)
            self.shift = shift.reshape(-1, shift.shape[-1])[:, :dim].copy()

        self.shuffle = None

        if 6 <= func_num <= 8:
            self.shuffle = np.loadtxt(
                DATA_DIR / f"shuffle_data_{func_num}_D{dim}.txt"
            ).astype(int)


class _State:
    """Emulates the C code's global scratch vector ``y``."""

    def __init__(self, dim: int):
        self.y = [0.0] * dim


# ---------------------------------------------------------------------------
# shift / rotate (sr_func)
# ---------------------------------------------------------------------------

def _sr(x, nx, os_, mr, rate, s_flag, r_flag, st):
    """Port of sr_func; also updates the emulated global y when r_flag == 1."""
    if s_flag == 1:
        shifted = [(x[i] - os_[i]) * rate for i in range(nx)]
    else:
        shifted = [x[i] * rate for i in range(nx)]

    if r_flag == 1:
        for i in range(nx):
            st.y[i] = shifted[i]

        return [
            sum(shifted[j] * mr[i][j] for j in range(nx)) for i in range(nx)
        ]

    return shifted


# ---------------------------------------------------------------------------
# basic functions: f(x, nx, os, mr, s_flag, r_flag, st) -> float
# ---------------------------------------------------------------------------

def _ellips(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    return sum(10.0 ** (6.0 * i / (nx - 1)) * z[i] * z[i] for i in range(nx))


def _bent_cigar(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    return z[0] * z[0] + sum(1e6 * z[i] * z[i] for i in range(1, nx))


def _discus(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    return 1e6 * z[0] * z[0] + sum(z[i] * z[i] for i in range(1, nx))


def _rosenbrock(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 2.048 / 100.0, s, r, st)
    z[0] += 1.0
    f = 0.0

    for i in range(nx - 1):
        z[i + 1] += 1.0
        tmp1 = z[i] * z[i] - z[i + 1]
        tmp2 = z[i] - 1.0
        f += 100.0 * tmp1 * tmp1 + tmp2 * tmp2

    return f


def _ackley(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    sum1 = sum(v * v for v in z)
    sum2 = sum(math.cos(2.0 * PI * v) for v in z)
    sum1 = -0.2 * math.sqrt(sum1 / nx)
    sum2 /= nx
    return E - 20.0 * math.exp(sum1) - math.exp(sum2) + 20.0


def _griewank(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 600.0 / 100.0, s, r, st)
    total = 0.0
    prod = 1.0

    for i in range(nx):
        total += z[i] * z[i]
        prod *= math.cos(z[i] / math.sqrt(1.0 + i))

    return 1.0 + total / 4000.0 - prod


def _rastrigin(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 5.12 / 100.0, s, r, st)
    return sum(v * v - 10.0 * math.cos(2.0 * PI * v) + 10.0 for v in z)


def _schwefel(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1000.0 / 100.0, s, r, st)
    f = 0.0

    for i in range(nx):
        z[i] += 4.209687462275036e+002

        if z[i] > 500:
            f -= (500.0 - math.fmod(z[i], 500)) * math.sin(
                math.pow(500.0 - math.fmod(z[i], 500), 0.5)
            )
            tmp = (z[i] - 500.0) / 100
            f += tmp * tmp / nx
        elif z[i] < -500:
            f -= (-500.0 + math.fmod(abs(z[i]), 500)) * math.sin(
                math.pow(500.0 - math.fmod(abs(z[i]), 500), 0.5)
            )
            tmp = (z[i] + 500.0) / 100
            f += tmp * tmp / nx
        else:
            f -= z[i] * math.sin(math.pow(abs(z[i]), 0.5))

    return f + 4.189828872724338e+002 * nx


def _grie_rosen(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 5.0 / 100.0, s, r, st)
    z[0] += 1.0
    f = 0.0

    for i in range(nx - 1):
        z[i + 1] += 1.0
        tmp1 = z[i] * z[i] - z[i + 1]
        tmp2 = z[i] - 1.0
        temp = 100.0 * tmp1 * tmp1 + tmp2 * tmp2
        f += (temp * temp) / 4000.0 - math.cos(temp) + 1.0

    tmp1 = z[nx - 1] * z[nx - 1] - z[0]
    tmp2 = z[nx - 1] - 1.0
    temp = 100.0 * tmp1 * tmp1 + tmp2 * tmp2
    return f + (temp * temp) / 4000.0 - math.cos(temp) + 1.0


def _escaffer6(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    f = 0.0

    for i in range(nx - 1):
        a = z[i] * z[i] + z[i + 1] * z[i + 1]
        temp1 = math.sin(math.sqrt(a)) ** 2
        temp2 = 1.0 + 0.001 * a
        f += 0.5 + (temp1 - 0.5) / (temp2 * temp2)

    a = z[nx - 1] * z[nx - 1] + z[0] * z[0]
    temp1 = math.sin(math.sqrt(a)) ** 2
    temp2 = 1.0 + 0.001 * a
    return f + 0.5 + (temp1 - 0.5) / (temp2 * temp2)


def _happycat(x, nx, os_, mr, s, r, st):
    alpha = 1.0 / 8.0
    z = _sr(x, nx, os_, mr, 5.0 / 100.0, s, r, st)
    r2 = 0.0
    sum_z = 0.0

    for i in range(nx):
        z[i] = z[i] - 1.0
        r2 += z[i] * z[i]
        sum_z += z[i]

    return (
        math.pow(abs(r2 - nx), 2 * alpha)
        + (0.5 * r2 + sum_z) / nx
        + 0.5
    )


def _hgbat(x, nx, os_, mr, s, r, st):
    alpha = 1.0 / 4.0
    z = _sr(x, nx, os_, mr, 5.0 / 100.0, s, r, st)
    r2 = 0.0
    sum_z = 0.0

    for i in range(nx):
        z[i] = z[i] - 1.0
        r2 += z[i] * z[i]
        sum_z += z[i]

    return (
        math.pow(abs(math.pow(r2, 2.0) - math.pow(sum_z, 2.0)), 2 * alpha)
        + (0.5 * r2 + sum_z) / nx
        + 0.5
    )


def _schaffer_f7(x, nx, os_, mr, s, r, st):
    # NOTE (official quirk): the loop reads the *global* y, not z. For the
    # stand-alone F3 call (r = 1) that is the shifted, un-rotated vector; for
    # the hybrid component (r = 0) it is the shuffled vector from index 0.
    _sr(x, nx, os_, mr, 1.0, s, r, st)
    f = 0.0

    for i in range(nx - 1):
        zi = math.pow(st.y[i] * st.y[i] + st.y[i + 1] * st.y[i + 1], 0.5)
        tmp = math.sin(50.0 * math.pow(zi, 0.2))
        f += math.pow(zi, 0.5) + math.pow(zi, 0.5) * tmp * tmp

    return f * f / (nx - 1) / (nx - 1)


def _step_rastrigin(x, nx, os_, mr, s, r, st):
    # The C code edits y here, but sr_func overwrites y immediately afterwards,
    # so the edit never reaches the result.
    z = _sr(x, nx, os_, mr, 5.12 / 100.0, s, r, st)
    return sum(v * v - 10.0 * math.cos(2.0 * PI * v) + 10.0 for v in z)


def _levy(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    w = [1.0 + (z[i] - 0.0) / 4.0 for i in range(nx)]

    term1 = math.pow(math.sin(PI * w[0]), 2)
    term3 = math.pow(w[nx - 1] - 1, 2) * (
        1 + math.pow(math.sin(2 * PI * w[nx - 1]), 2)
    )

    total = 0.0

    for i in range(nx - 1):
        wi = w[i]
        total += math.pow(wi - 1, 2) * (
            1 + 10 * math.pow(math.sin(PI * wi + 1), 2)
        )

    return term1 + total + term3


def _zakharov(x, nx, os_, mr, s, r, st):
    z = _sr(x, nx, os_, mr, 1.0, s, r, st)
    sum1 = 0.0
    sum2 = 0.0

    for i in range(nx):
        sum1 += z[i] ** 2
        sum2 += 0.5 * (i + 1) * z[i]

    return sum1 + sum2 ** 2 + sum2 ** 4


def _katsuura(x, nx, os_, mr, s, r, st):
    f = 1.0
    tmp3 = math.pow(1.0 * nx, 1.2)
    z = _sr(x, nx, os_, mr, 5.0 / 100.0, s, r, st)

    for i in range(nx):
        temp = 0.0

        for j in range(1, 33):
            tmp1 = math.pow(2.0, j)
            tmp2 = tmp1 * z[i]
            temp += abs(tmp2 - math.floor(tmp2 + 0.5)) / tmp1

        f *= math.pow(1.0 + (i + 1) * temp, 10.0 / tmp3)

    tmp1 = 10.0 / nx / nx
    return f * tmp1 - tmp1


# ---------------------------------------------------------------------------
# hybrid functions
# ---------------------------------------------------------------------------

def _group_sizes(proportions: Sequence[float], nx: int) -> List[int]:
    sizes = [math.ceil(p * nx) for p in proportions[:-1]]
    sizes.append(nx - sum(sizes))
    return sizes


def _hybrid(components, proportions, x, nx, os_, mr, shuffle, st):
    sizes = _group_sizes(proportions, nx)
    starts = [0]

    for size in sizes[:-1]:
        starts.append(starts[-1] + size)

    z = _sr(x, nx, os_, mr, 1.0, 1, 1, st)

    for i in range(nx):
        st.y[i] = z[shuffle[i] - 1]

    total = 0.0

    for func, start, size in zip(components, starts, sizes):
        # the component sees y[start:start+size] as its input vector
        part = st.y[start:start + size]
        total += func(part, size, os_, mr, 0, 0, st)

    return total


def _hf02(x, nx, os_, mr, shuffle, st):
    return _hybrid(
        [_bent_cigar, _hgbat, _rastrigin], [0.4, 0.4, 0.2],
        x, nx, os_, mr, shuffle, st,
    )


def _hf10(x, nx, os_, mr, shuffle, st):
    return _hybrid(
        [_hgbat, _katsuura, _ackley, _rastrigin, _schwefel, _schaffer_f7],
        [0.1, 0.2, 0.2, 0.2, 0.1, 0.2],
        x, nx, os_, mr, shuffle, st,
    )


def _hf06(x, nx, os_, mr, shuffle, st):
    return _hybrid(
        [_katsuura, _happycat, _grie_rosen, _schwefel, _ackley],
        [0.3, 0.2, 0.2, 0.1, 0.2],
        x, nx, os_, mr, shuffle, st,
    )


# ---------------------------------------------------------------------------
# composition functions
# ---------------------------------------------------------------------------

def _cf_cal(x, nx, shifts, delta, bias, fit):
    cf_num = len(fit)
    w = []
    w_max = 0.0

    for i in range(cf_num):
        fit[i] += bias[i]
        wi = sum((x[j] - shifts[i][j]) ** 2 for j in range(nx))

        if wi != 0:
            wi = math.pow(1.0 / wi, 0.5) * math.exp(
                -wi / 2.0 / nx / math.pow(delta[i], 2.0)
            )
        else:
            wi = INF

        w.append(wi)

        if wi > w_max:
            w_max = wi

    w_sum = sum(w)

    if w_max == 0:
        w = [1.0] * cf_num
        w_sum = float(cf_num)

    return sum(w[i] / w_sum * fit[i] for i in range(cf_num))


def _composition(spec, x, nx, shifts, mats, st):
    """spec: list of (function, rotate_flag, scale) per component."""
    fit = []

    for i, (func, r_flag, scale) in enumerate(spec["components"]):
        value = func(x, nx, shifts[i], mats[i], 1, r_flag, st)
        fit.append(scale(value))

    return _cf_cal(x, nx, shifts, spec["delta"], spec["bias"], fit)


def _scaled(numerator, denominator):
    return lambda v: numerator * v / denominator


_identity = lambda v: v

_CF = {
    9: {
        "components": [
            (_rosenbrock, 1, _scaled(10000, 1e+4)),
            (_ellips, 1, _scaled(10000, 1e+10)),
            (_bent_cigar, 1, _scaled(10000, 1e+30)),
            (_discus, 1, _scaled(10000, 1e+10)),
            (_ellips, 0, _scaled(10000, 1e+10)),
        ],
        "delta": [10, 20, 30, 40, 50],
        "bias": [0, 200, 300, 100, 400],
    },
    10: {
        "components": [
            (_schwefel, 0, _identity),
            (_rastrigin, 1, _identity),
            (_hgbat, 1, _identity),
        ],
        "delta": [20, 10, 10],
        "bias": [0, 200, 100],
    },
    11: {
        "components": [
            (_escaffer6, 1, _scaled(10000, 2e+7)),
            (_schwefel, 1, _identity),
            (_griewank, 1, _scaled(1000, 100)),
            (_rosenbrock, 1, _identity),
            (_rastrigin, 1, _scaled(10000, 1e+3)),
        ],
        "delta": [20, 20, 30, 30, 20],
        "bias": [0, 200, 300, 400, 200],
    },
    12: {
        "components": [
            (_hgbat, 1, _scaled(10000, 1000)),
            (_rastrigin, 1, _scaled(10000, 1e+3)),
            (_schwefel, 1, _scaled(10000, 4e+3)),
            (_bent_cigar, 1, _scaled(10000, 1e+30)),
            (_ellips, 1, _scaled(10000, 1e+10)),
            (_escaffer6, 1, _scaled(10000, 2e+7)),
        ],
        "delta": [10, 20, 30, 40, 50, 60],
        "bias": [0, 300, 500, 100, 400, 200],
    },
}

_BASIC = {
    1: _zakharov,
    2: _rosenbrock,
    3: _schaffer_f7,
    4: _step_rastrigin,
    5: _levy,
}

_HYBRID = {6: _hf02, 7: _hf10, 8: _hf06}


class CEC2022Function:
    """One CEC 2022 function at a fixed dimension; call it with a vector.

    ``f(x)`` returns the function value (including the bias F*), and
    ``f.objective(x)`` returns ``[value]`` so it can be passed to SPEA2.
    ``f.error(x)`` returns ``f(x) - F*``.
    """

    lower = LOWER
    upper = UPPER

    def __init__(self, func_num: int, dim: int):
        self._data = _Data(func_num, dim)   # validates func_num and dim
        self.func_num = func_num
        self.dim = dim
        self.f_star = F_STAR[func_num]
        self._mats = (
            [self._data.M[i].tolist() for i in range(len(self._data.M))]
            if func_num >= 9 else None
        )
        self._shifts = (
            [self._data.shift[i].tolist() for i in range(len(self._data.shift))]
            if func_num >= 9 else None
        )
        self._basic_m = self._data.M.tolist() if func_num < 9 else None
        self._basic_o = self._data.shift.tolist() if func_num < 9 else None
        self._shuffle = (
            self._data.shuffle.tolist() if self._data.shuffle is not None else None
        )

    @property
    def optimum(self) -> List[float]:
        """The shifted global optimum o (first component for compositions)."""
        if self.func_num < 9:
            return list(self._basic_o)

        return list(self._shifts[0])

    def __call__(self, x: Sequence[float]) -> float:
        if len(x) != self.dim:
            raise ValueError(f"Expected {self.dim} variables, got {len(x)}")

        nx = self.dim
        x = [float(v) for v in x]
        st = _State(nx)
        f = self.func_num

        if f in _BASIC:
            value = _BASIC[f](
                x, nx, self._basic_o, self._basic_m, 1, 1, st
            )
        elif f in _HYBRID:
            value = _HYBRID[f](
                x, nx, self._basic_o, self._basic_m, self._shuffle, st
            )
        else:
            value = _composition(
                _CF[f], x, nx, self._shifts, self._mats, st
            )

        return value + self.f_star

    def error(self, x: Sequence[float]) -> float:
        return self(x) - self.f_star

    def objective(self, x: Sequence[float]) -> List[float]:
        return [self(x)]


def load_seeds() -> np.ndarray:
    """The 1000 official random seeds."""
    return np.loadtxt(DATA_DIR / "Rand_Seeds.txt").astype(int)


def run_seed(dim: int, func_num: int, run_id: int, runs: int = 30) -> int:
    """Official seed for a run (``seed_ind`` rule of the technical report).

    seed_ind = (problem_size / 10 * func_no * runs + run_id) - runs
    seed_ind = mod(seed_ind, 1000) + 1   (1-based index into Rand_Seeds)
    """
    seed_ind = (dim // 10 * func_num * runs + run_id) - runs
    seed_ind = seed_ind % 1000

    return int(load_seeds()[seed_ind])
