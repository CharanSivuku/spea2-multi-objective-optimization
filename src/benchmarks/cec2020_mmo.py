"""CEC 2020 multimodal multi-objective (MMO) test problems: 24 problems.

Port of the organisers' MATLAB suite (`MM_testfunctions/functions/*.m`) together
with the per-problem settings of their example harness (`main.m`): variable
bounds, hypervolume reference point and the number of Pareto sets to find
(`N_ops`). The reference Pareto sets / fronts come from the organisers' `.mat`
files, converted once to CSV in `data/cec2020_mmo/<name>_PS.csv` and
`<name>_PF.csv`.

All objectives are minimised. A MMO problem has several Pareto sets (PS) that map
to the same, or a similar, Pareto front, so algorithms are assessed both in
objective space (IGDF, 1/HV) and in decision space (IGDX, 1/PSP).

Problems whose name ends in ``_l`` share the objective function of the problem
without the suffix; only their reference data differ (they also contain the
*local* Pareto sets and fronts that have to be found).

Evaluation protocol (technical report, section 2.2): 21 runs, population size
``200 * N_ops``, maximum evaluations ``10000 * N_ops``.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence

import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "cec2020_mmo"

_LOG2_10 = math.log10(2.0)


# ---------------------------------------------------------------------------
# two-variable and three-variable bi-objective problems
# ---------------------------------------------------------------------------

def mmf1(x: Sequence[float]) -> List[float]:
    a = abs(x[0] - 2.0)
    return [a, 1.0 - math.sqrt(a) + 2.0 * (x[1] - math.sin(6.0 * math.pi * a + math.pi)) ** 2]


def mmf1_e(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    if x1 < 2.0:
        a = 2.0 - x1
        return [a, 1.0 - math.sqrt(a) + 2.0 * (x2 - math.sin(6.0 * math.pi * a + math.pi)) ** 2]

    a = x1 - 2.0
    return [
        a,
        1.0 - math.sqrt(a)
        + 2.0 * (x2 - math.exp(x1) * math.sin(6.0 * math.pi * a + math.pi)) ** 2,
    ]


def mmf2(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    if x2 > 1.0:
        x2 -= 1.0

    y2 = x2 - math.sqrt(x1)

    return [
        x1,
        1.0 - math.sqrt(x1)
        + 2.0 * (4.0 * y2 ** 2 - 2.0 * math.cos(20.0 * y2 * math.pi / math.sqrt(2.0)) + 2.0),
    ]


def mmf4(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    if x2 > 1.0:
        x2 -= 1.0

    return [
        abs(x1),
        1.0 - x1 ** 2 + 2.0 * (x2 - math.sin(math.pi * abs(x1))) ** 2,
    ]


def mmf5(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    if x2 > 1.0:
        x2 -= 2.0

    a = abs(x1 - 2.0)

    return [a, 1.0 - math.sqrt(a) + 2.0 * (x2 - math.sin(6.0 * math.pi * a + math.pi)) ** 2]


def mmf7(x: Sequence[float]) -> List[float]:
    a = abs(x[0] - 2.0)
    shape = (
        0.3 * a ** 2 * math.cos(24.0 * math.pi * a + 4.0 * math.pi) + 0.6 * a
    ) * math.sin(6.0 * math.pi * a + math.pi)

    return [a, 1.0 - math.sqrt(a) + (x[1] - shape) ** 2]


def mmf8(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    if x2 > 4.0:
        x2 -= 4.0

    s = math.sin(abs(x1))

    return [s, math.sqrt(1.0 - s ** 2) + 2.0 * (x2 - (s + abs(x1))) ** 2]


def mmf10(x: Sequence[float]) -> List[float]:
    g = (
        2.0
        - math.exp(-(((x[1] - 0.2) / 0.004) ** 2))
        - 0.8 * math.exp(-(((x[1] - 0.6) / 0.4) ** 2))
    )

    return [x[0], g / x[0]]


def mmf11(x: Sequence[float]) -> List[float]:
    num_of_peak = 2
    temp1 = math.sin(num_of_peak * math.pi * x[1]) ** 6
    temp2 = math.exp(-2.0 * _LOG2_10 * ((x[1] - 0.1) / 0.8) ** 2)
    g = 2.0 - temp2 * temp1

    return [x[0], g / x[0]]


def mmf12(x: Sequence[float]) -> List[float]:
    q = 4
    alfa = 2
    f1 = x[0]
    num_of_peak = 2
    g = 2.0 - (math.sin(num_of_peak * math.pi * x[1]) ** 6) * math.exp(
        -2.0 * _LOG2_10 * ((x[1] - 0.1) / 0.8) ** 2
    )
    h = 1.0 - (f1 / g) ** alfa - (f1 / g) * math.sin(2.0 * math.pi * q * f1)

    return [f1, g * h]


def mmf13(x: Sequence[float]) -> List[float]:
    t = x[1] + math.sqrt(x[2])
    g = 2.0 - math.exp(-2.0 * _LOG2_10 * ((t - 0.1) / 0.8) ** 2) * math.sin(2.0 * math.pi * t) ** 6

    return [x[0], g / x[0]]


# ---------------------------------------------------------------------------
# scalable (M-objective) problems, DTLZ2-like geometry
# ---------------------------------------------------------------------------

def _dtlz2_like(x: Sequence[float], g: float, m: int) -> List[float]:
    """y = (1+g) * fliplr(cumprod([1, cos(x(1:M-1) pi/2)])) .* [1, sin(x(M-1:-1:1) pi/2)]"""
    cos_part = [1.0]

    for i in range(m - 1):
        cos_part.append(cos_part[-1] * math.cos(x[i] * math.pi / 2.0))

    cos_part.reverse()
    sin_part = [1.0] + [math.sin(x[i] * math.pi / 2.0) for i in range(m - 2, -1, -1)]

    return [(1.0 + g) * c * s for c, s in zip(cos_part, sin_part)]


def mmf14(x: Sequence[float], m: int = 3, num_of_peak: int = 2) -> List[float]:
    g = 2.0 - math.sin(num_of_peak * math.pi * x[-1]) ** 2
    return _dtlz2_like(x, g, m)


def mmf14_a(x: Sequence[float], m: int = 3, num_of_peak: int = 2) -> List[float]:
    x_g = x[-1] - 0.5 * math.sin(math.pi * x[-2])
    g = 2.0 - math.sin(num_of_peak * math.pi * (x_g + 1.0 / (2 * num_of_peak))) ** 2
    return _dtlz2_like(x, g, m)


def mmf15(x: Sequence[float], m: int = 3, num_of_peak: int = 2) -> List[float]:
    g = 2.0 - math.exp(-2.0 * _LOG2_10 * ((x[-1] - 0.1) / 0.8) ** 2) * math.sin(
        num_of_peak * math.pi * x[-1]
    ) ** 2
    return _dtlz2_like(x, g, m)


def mmf15_a(x: Sequence[float], m: int = 3, num_of_peak: int = 2) -> List[float]:
    t = -0.5 * math.sin(math.pi * x[-2]) + x[-1]
    u = t + 1.0 / (2 * num_of_peak)
    g = 2.0 - math.exp(-2.0 * _LOG2_10 * ((u - 0.1) / 0.8) ** 2) * math.sin(
        num_of_peak * math.pi * u
    ) ** 2
    return _dtlz2_like(x, g, m)


def _mmf16(x: Sequence[float], num_of_g_peak: int, num_of_l_peak: int, m: int = 3) -> List[float]:
    last = x[-1]

    if 0.0 <= last < 0.5:
        g = 2.0 - math.sin(2 * num_of_g_peak * math.pi * last) ** 2
    elif 0.5 <= last <= 1.0:
        g = 2.0 - math.exp(-2.0 * _LOG2_10 * ((last - 0.1) / 0.8) ** 2) * math.sin(
            2 * num_of_l_peak * math.pi * last
        ) ** 2
    else:
        raise ValueError("MMF16 variables must lie in [0, 1]")

    return _dtlz2_like(x, g, m)


def mmf16_l1(x: Sequence[float]) -> List[float]:
    return _mmf16(x, 2, 1)


def mmf16_l2(x: Sequence[float]) -> List[float]:
    return _mmf16(x, 1, 2)


def mmf16_l3(x: Sequence[float]) -> List[float]:
    return _mmf16(x, 2, 2)


# ---------------------------------------------------------------------------
# registry (settings taken from the organisers' main.m)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MMOProblem:
    name: str
    objective: Callable[[Sequence[float]], List[float]]
    n_var: int
    n_obj: int
    lower: List[float]
    upper: List[float]
    hv_reference_point: List[float]
    n_ops: int          # number of Pareto sets (global + local) to be found
    n_global: int
    n_local: int

    @property
    def population_size(self) -> int:
        return 200 * self.n_ops

    @property
    def max_evaluations(self) -> int:
        return 10000 * self.n_ops

    @property
    def generations(self) -> int:
        """Generations so that new evaluations equal the MaxFES budget."""
        return self.max_evaluations // self.population_size

    def reference_ps(self) -> np.ndarray:
        return np.loadtxt(DATA_DIR / f"{self.name}_PS.csv", delimiter=",", ndmin=2)

    def reference_pf(self) -> np.ndarray:
        return np.loadtxt(DATA_DIR / f"{self.name}_PF.csv", delimiter=",", ndmin=2)


def _p(name, fn, n_var, n_obj, lower, upper, repoint, n_global, n_local):
    return MMOProblem(
        name, fn, n_var, n_obj, list(lower), list(upper), list(repoint),
        n_global + n_local, n_global, n_local,
    )


_PI = math.pi

_SPECS = [
    # name, fn, n_var, n_obj, lower, upper, repoint, N_global, N_local
    ("MMF1", mmf1, 2, 2, [1, -1], [3, 1], [1.1, 1.1], 2, 0),
    ("MMF2", mmf2, 2, 2, [0, 0], [1, 2], [1.1, 1.1], 2, 0),
    ("MMF4", mmf4, 2, 2, [-1, 0], [1, 2], [1.1, 1.1], 2, 0),
    ("MMF5", mmf5, 2, 2, [1, -1], [3, 3], [1.1, 1.1], 2, 0),
    ("MMF7", mmf7, 2, 2, [1, -1], [3, 1], [1.1, 1.1], 2, 0),
    ("MMF8", mmf8, 2, 2, [-_PI, 0], [_PI, 9], [1.1, 1.1], 2, 0),
    ("MMF10", mmf10, 2, 2, [0.1, 0.1], [1.1, 1.1], [1.21, 13.2], 1, 0),
    ("MMF11", mmf11, 2, 2, [0.1, 0.1], [1.1, 1.1], [1.21, 15.4], 1, 0),
    ("MMF12", mmf12, 2, 2, [0, 0], [1, 1], [1.54, 1.1], 1, 0),
    ("MMF13", mmf13, 3, 2, [0.1] * 3, [1.1] * 3, [1.54, 15.4], 1, 0),
    ("MMF14", mmf14, 3, 3, [0] * 3, [1] * 3, [2.2] * 3, 2, 0),
    ("MMF15", mmf15, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 1, 0),
    ("MMF1_e", mmf1_e, 2, 2, [1, -20], [3, 20], [1.1, 1.1], 2, 0),
    ("MMF14_a", mmf14_a, 3, 3, [0] * 3, [1] * 3, [2.2] * 3, 2, 0),
    ("MMF15_a", mmf15_a, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 1, 0),
    ("MMF10_l", mmf10, 2, 2, [0.1, 0.1], [1.1, 1.1], [1.21, 13.2], 1, 1),
    ("MMF11_l", mmf11, 2, 2, [0.1, 0.1], [1.1, 1.1], [1.21, 15.4], 1, 1),
    ("MMF12_l", mmf12, 2, 2, [0, 0], [1, 1], [1.54, 1.1], 1, 1),
    ("MMF13_l", mmf13, 3, 2, [0.1] * 3, [1.1] * 3, [1.54, 15.4], 1, 1),
    ("MMF15_l", mmf15, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 1, 1),
    ("MMF15_a_l", mmf15_a, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 1, 1),
    ("MMF16_l1", mmf16_l1, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 2, 1),
    ("MMF16_l2", mmf16_l2, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 1, 2),
    ("MMF16_l3", mmf16_l3, 3, 3, [0] * 3, [1] * 3, [2.5] * 3, 2, 2),
]

MMO_PROBLEMS = {spec[0]: _p(*spec) for spec in _SPECS}

MMO_NAMES = [spec[0] for spec in _SPECS]


def get_problem(name: str) -> MMOProblem:
    try:
        return MMO_PROBLEMS[name]
    except KeyError:
        raise ValueError(f"Unknown CEC2020 MMO problem: {name}") from None
