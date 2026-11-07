
"""Classical multi-objective benchmark functions."""

import math
import random
from typing import List, Sequence


def _sample_line(n: int):
    if n < 2:
        raise ValueError("n must be at least 2")
    return range(n)


# =========================================================
# Binh (1)
# =========================================================

def binh1(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [
        x1**2 + x2**2,
        (x1 - 5.0)**2 + (x2 - 5.0)**2
    ]


def binh1_reference_front(n: int = 1000) -> List[List[float]]:
    return [
        [2.0 * t**2, 2.0 * (t - 5.0)**2]
        for t in (5.0 * i / (n - 1) for i in _sample_line(n))
    ]


# =========================================================
# Deb
# =========================================================

def deb(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [x1, 1.0 - x1**2]


def deb_reference_front(n: int = 1000) -> List[List[float]]:
    return [
        [t, 1.0 - t**2]
        for t in (i / (n - 1) for i in _sample_line(n))
    ]


# =========================================================
# Deb (2)
# =========================================================

def deb2(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    f1 = x1
    g = 1.0 + 10.0 * x2
    ratio = f1 / g

    h = (
        1.0
        - ratio**2
        - ratio * math.sin(12.0 * math.pi * f1)
    )

    return [f1, g * h]


def deb2_reference_front(n: int = 3000) -> List[List[float]]:
    """Non-dominated part of the x2 = 0 curve.

    With x2 = 0 (g = 1) the curve f2 = 1 - t^2 - t sin(12 pi t) is
    multimodal; only points whose f2 is below every f2 at smaller f1 are
    Pareto optimal. (The whole curve was returned before, which included
    dominated points and inflated IGD.)
    """
    front = []
    best_f2 = float("inf")

    for i in _sample_line(n):
        t = i / (n - 1)
        f2 = 1.0 - t**2 - t * math.sin(12.0 * math.pi * t)

        if f2 < best_f2:
            front.append([t, f2])
            best_f2 = f2

    return front


# =========================================================
# Fonseca
# =========================================================

def fonseca(x: Sequence[float]) -> List[float]:
    x1, x2 = x

    f1 = 1.0 - math.exp(
        -((x1 - 1.0)**2 + (x2 + 1.0)**2)
    )

    f2 = 1.0 - math.exp(
        -((x1 + 1.0)**2 + (x2 - 1.0)**2)
    )

    return [f1, f2]


def fonseca_reference_front(n: int = 1000) -> List[List[float]]:
    return [
        fonseca([t, -t])
        for t in (
            -1.0 + 2.0 * i / (n - 1)
            for i in _sample_line(n)
        )
    ]


# =========================================================
# Fonseca (2)
# =========================================================

def fonseca2(x: Sequence[float]) -> List[float]:
    n = len(x)

    if n != 2:
        raise ValueError("Fonseca2 requires exactly 2 variables.")

    shift = 1.0 / math.sqrt(n)

    f1 = 1.0 - math.exp(
        -sum((xi - shift)**2 for xi in x)
    )

    f2 = 1.0 - math.exp(
        -sum((xi + shift)**2 for xi in x)
    )

    return [f1, f2]


def fonseca2_reference_front(n: int = 1000) -> List[List[float]]:
    shift = 1.0 / math.sqrt(2.0)

    return [
        fonseca2([t, t])
        for t in (
            -shift + 2.0 * shift * i / (n - 1)
            for i in _sample_line(n)
        )
    ]


# =========================================================
# Kursawe
# =========================================================

def kursawe(x: Sequence[float]) -> List[float]:
    if len(x) != 3:
        raise ValueError("Kursawe requires exactly 3 variables.")

    f1 = sum(
        -10.0 * math.exp(
            -0.2 * math.sqrt(x[i]**2 + x[i + 1]**2)
        )
        for i in range(2)
    )

    f2 = sum(
        abs(xi)**0.8 + 5.0 * math.sin(xi**3)
        for xi in x
    )

    return [f1, f2]


def kursawe_reference_front(
    n_samples: int = 200000,
    seed: int = 42,
) -> List[List[float]]:
    """Sampled approximation of the Kursawe Pareto front."""

    rng = random.Random(seed)
    candidates = []

    for _ in range(n_samples):
        x = [
            rng.uniform(-5.0, 5.0)
            for _ in range(3)
        ]
        candidates.append(kursawe(x))

    candidates.sort(key=lambda p: p[0])

    front = []
    best_f2 = float("inf")

    for point in candidates:
        if point[1] < best_f2:
            front.append(point)
            best_f2 = point[1]

    return front
