
"""DTLZ1--DTLZ7 benchmark problems.

All problems use minimization and decision variables in [0, 1].
Three objectives are used by default.
"""

from __future__ import annotations

import math
from typing import Callable, List, Sequence

Vector = Sequence[float]


def _validate(x: Vector, n_obj: int) -> None:
    if n_obj < 2:
        raise ValueError("DTLZ problems require at least two objectives")

    if len(x) < n_obj:
        raise ValueError("n_var must be at least n_obj")

    if any(not 0.0 <= float(v) <= 1.0 for v in x):
        raise ValueError("DTLZ decision variables must be in [0, 1]")


def _g1(z: Vector) -> float:
    return 100.0 * (
        len(z)
        + sum(
            (v - 0.5) ** 2
            - math.cos(20.0 * math.pi * (v - 0.5))
            for v in z
        )
    )


def _g2(z: Vector) -> float:
    return sum((v - 0.5) ** 2 for v in z)


def _g6(z: Vector) -> float:
    return sum(v ** 0.1 for v in z)


def _spherical_objectives(
    theta: Sequence[float],
    scale: float,
    n_obj: int
) -> List[float]:

    result = []

    for i in range(n_obj):
        value = scale

        for j in range(n_obj - i - 1):
            value *= math.cos(theta[j] * math.pi / 2.0)

        if i > 0:
            value *= math.sin(
                theta[n_obj - i - 1] * math.pi / 2.0
            )

        result.append(value)

    return result


# --------------------------------------------------
# DTLZ1
# --------------------------------------------------

def dtlz1(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    m = n_obj
    g = _g1(x[m - 1:])
    f = []

    for i in range(m):
        value = 0.5 * (1.0 + g)

        for j in range(m - i - 1):
            value *= x[j]

        if i > 0:
            value *= 1.0 - x[m - i - 1]

        f.append(value)

    return f


# --------------------------------------------------
# DTLZ2
# --------------------------------------------------

def dtlz2(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    return _spherical_objectives(
        x[:n_obj - 1],
        1.0 + _g2(x[n_obj - 1:]),
        n_obj
    )


# --------------------------------------------------
# DTLZ3
# --------------------------------------------------

def dtlz3(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    return _spherical_objectives(
        x[:n_obj - 1],
        1.0 + _g1(x[n_obj - 1:]),
        n_obj
    )


# --------------------------------------------------
# DTLZ4
# --------------------------------------------------

def dtlz4(
    x: Vector,
    n_obj: int = 3,
    alpha: float = 100.0
) -> List[float]:

    _validate(x, n_obj)

    theta = [
        v ** alpha
        for v in x[:n_obj - 1]
    ]

    return _spherical_objectives(
        theta,
        1.0 + _g2(x[n_obj - 1:]),
        n_obj
    )


# --------------------------------------------------
# DTLZ5 and DTLZ6 helper
# --------------------------------------------------

def _dtlz5_6_angles(
    x: Vector,
    n_obj: int,
    g: float
) -> List[float]:

    theta = [float(x[0])]

    theta.extend(
        (1.0 + 2.0 * g * float(v)) / (2.0 * (1.0 + g))
        for v in x[1:n_obj - 1]
    )

    return theta


# --------------------------------------------------
# DTLZ5
# --------------------------------------------------

def dtlz5(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    g = _g2(x[n_obj - 1:])

    return _spherical_objectives(
        _dtlz5_6_angles(x, n_obj, g),
        1.0 + g,
        n_obj
    )


# --------------------------------------------------
# DTLZ6
# --------------------------------------------------

def dtlz6(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    g = _g6(x[n_obj - 1:])

    return _spherical_objectives(
        _dtlz5_6_angles(x, n_obj, g),
        1.0 + g,
        n_obj
    )


# --------------------------------------------------
# DTLZ7
# --------------------------------------------------

def dtlz7(x: Vector, n_obj: int = 3) -> List[float]:
    _validate(x, n_obj)

    m = n_obj
    first = [float(v) for v in x[:m - 1]]
    tail = x[m - 1:]

    if not tail:
        raise ValueError(
            "DTLZ7 requires at least one distance variable"
        )

    g = 1.0 + 9.0 * sum(tail) / len(tail)

    h = m - sum(
        v / (1.0 + g)
        * (1.0 + math.sin(3.0 * math.pi * v))
        for v in first
    )

    return first + [(1.0 + g) * h]


# --------------------------------------------------
# DTLZ function registry
# --------------------------------------------------

DTLZ_FUNCTIONS: dict[
    str, Callable[..., List[float]]
] = {
    "DTLZ1": dtlz1,
    "DTLZ2": dtlz2,
    "DTLZ3": dtlz3,
    "DTLZ4": dtlz4,
    "DTLZ5": dtlz5,
    "DTLZ6": dtlz6,
    "DTLZ7": dtlz7,
}


# --------------------------------------------------
# Reference front: DTLZ1
# --------------------------------------------------

def _simplex_front(
    n_obj: int,
    divisions: int
) -> List[List[float]]:

    points: List[List[float]] = []

    def rec(
        prefix: List[int],
        remaining: int,
        slots: int
    ) -> None:

        if slots == 1:
            points.append([
                0.5 * v / divisions
                for v in prefix + [remaining]
            ])
            return

        for value in range(remaining + 1):
            rec(
                prefix + [value],
                remaining - value,
                slots - 1
            )

    rec([], divisions, n_obj)

    return points


# --------------------------------------------------
# Reference front: DTLZ2, DTLZ3, DTLZ4
# --------------------------------------------------

def _sphere_front(
    n_obj: int,
    divisions: int
) -> List[List[float]]:

    if n_obj == 2:
        return [
            [
                math.cos(t * math.pi / (2 * divisions)),
                math.sin(t * math.pi / (2 * divisions))
            ]
            for t in range(divisions + 1)
        ]

    if n_obj == 3:
        points = []

        for i in range(divisions + 1):
            theta = i * math.pi / (2 * divisions)

            for j in range(divisions + 1):
                phi = j * math.pi / (2 * divisions)

                points.append([
                    math.cos(theta) * math.cos(phi),
                    math.cos(theta) * math.sin(phi),
                    math.sin(theta)
                ])

        return points

    points = []

    def rec(prefix: List[float], slots: int) -> None:
        if slots == 1:
            vec = prefix + [1.0]
            norm = math.sqrt(sum(v * v for v in vec))

            points.append([
                v / norm for v in vec
            ])

            return

        for k in range(divisions + 1):
            rec(
                prefix + [k / divisions],
                slots - 1
            )

    rec([], n_obj)

    return points


# --------------------------------------------------
# Remove dominated points
# --------------------------------------------------

def _nondominated(
    points: List[List[float]]
) -> List[List[float]]:

    result = []

    for i, point in enumerate(points):

        dominated = any(
            i != j
            and all(
                other[k] <= point[k]
                for k in range(len(point))
            )
            and any(
                other[k] < point[k]
                for k in range(len(point))
            )
            for j, other in enumerate(points)
        )

        if not dominated:
            result.append(point)

    return result


# --------------------------------------------------
# Reference front: DTLZ7
# --------------------------------------------------

def _dtlz7_reference_front(
    divisions: int
) -> List[List[float]]:
    """
    Sample the three-objective DTLZ7 Pareto front.

    On the Pareto front, g = 1.

    Therefore:

    f3 = 6
         - f1 * (1 + sin(3*pi*f1))
         - f2 * (1 + sin(3*pi*f2))

    The DTLZ7 Pareto front is disconnected.
    This function generates a sampled approximation.
    """

    candidates = []
    grid = max(20, divisions)

    for i in range(grid + 1):
        f1 = i / grid

        for j in range(grid + 1):
            f2 = j / grid

            f3 = (
                6.0
                - f1 * (
                    1.0 + math.sin(3.0 * math.pi * f1)
                )
                - f2 * (
                    1.0 + math.sin(3.0 * math.pi * f2)
                )
            )

            if f3 >= 0.0:
                candidates.append([f1, f2, f3])

    return _nondominated(candidates)


# --------------------------------------------------
# Generate reference front for any DTLZ problem
# --------------------------------------------------

def generate_dtlz_reference_front(
    name: str,
    n_obj: int = 3,
    divisions: int = 100
) -> List[List[float]]:

    key = name.upper()

    if key not in DTLZ_FUNCTIONS:
        raise ValueError(
            f"Unknown DTLZ problem: {name}"
        )

    if n_obj < 2:
        raise ValueError(
            "DTLZ problems require at least two objectives"
        )

    if divisions < 1:
        raise ValueError(
            "divisions must be at least 1"
        )

    if key == "DTLZ1":
        return _simplex_front(n_obj, divisions)

    if key in {"DTLZ2", "DTLZ3", "DTLZ4"}:
        return _sphere_front(n_obj, divisions)

    if key in {"DTLZ5", "DTLZ6"}:

        if n_obj == 2:
            return _sphere_front(2, divisions)

        points = []

        for i in range(divisions + 1):
            theta = i / divisions

            # First angle varies from 0 to 1.
            # Remaining transformed angles are 1/2 (i.e. pi/4) on the PF:
            # with g = 0, (1 + 2 g x) / (2 (1 + g)) = 1/2, so f1 = f2.
            # (This was 0.25 before, which put the reference front on a
            # different curve from the true DTLZ5/6 Pareto front.)
            angles = (
                [theta]
                + [0.5] * (n_obj - 2)
            )

            points.append(
                _spherical_objectives(
                    angles,
                    1.0,
                    n_obj
                )
            )

        return points

    if key == "DTLZ7":

        if n_obj != 3:
            raise NotImplementedError(
                "DTLZ7 reference-front sampler currently "
                "supports 3 objectives"
            )

        return _dtlz7_reference_front(divisions)

    raise ValueError(f"Unsupported benchmark: {name}")
