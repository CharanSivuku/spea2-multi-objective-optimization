"""Remaining classical multi-objective benchmarks (all objectives minimised).

Formulations follow the MOEA Framework `org.moeaframework.problem.misc`
classes (which aggregate the Van Veldhuizen test-problem suite) and were
cross-checked against the value ranges plotted in Benchmark_Comparison.pdf.

Reference fronts are analytical wherever the Pareto set can be derived
(Binh3, Laumanns, Murata, Rendon, Rendon2, Schaffer, Schaffer2, Viennet).
The others use documented numerical constructions:

* Srinivas   - Pareto-set candidates (x1 = -2.5, g2 line, g1 circle),
                feasibility- and ND-filtered, arc-length thinned.
* Tanaka     - boundary of the feasible region, ND-filtered, arc-length thinned.
* Quagliarella - dynamic-programming Minkowski sum of the per-variable
                 non-dominated sets (exact for separable sums).
* Viennet2   - weighted-sum minimisers of convex quadratics (exact for convex
                 problems), ND-filtered.

No front is obtained by random sampling of the decision space.

Constrained problems expose a `*_violation(x)` function returning the total
constraint violation (0 means feasible).
"""

import math
from functools import lru_cache
from typing import List, Sequence

import numpy as np


# =========================================================
# Helpers
# =========================================================

def _as_list(points) -> List[List[float]]:
    return [[float(v) for v in p] for p in np.asarray(points)]


def _nondominated_2d(points: np.ndarray) -> np.ndarray:
    """Non-dominated subset of 2-objective points (minimisation)."""
    order = np.lexsort((points[:, 1], points[:, 0]))
    sorted_points = points[order]

    keep = []
    best_f2 = np.inf

    for index, (f1, f2) in enumerate(sorted_points):
        if f2 < best_f2:
            keep.append(index)
            best_f2 = f2

    return sorted_points[keep]


def _nondominated(points: np.ndarray) -> np.ndarray:
    """Non-dominated subset for any number of objectives (O(n^2))."""
    points = np.unique(points, axis=0)

    if points.shape[1] == 2:
        return _nondominated_2d(points)

    keep = np.ones(len(points), dtype=bool)

    for i in range(len(points)):
        if not keep[i]:
            continue

        dominated = (
            np.all(points <= points[i], axis=1)
            & np.any(points < points[i], axis=1)
        )

        if dominated.any():
            keep[i] = False

    return points[keep]


def _thin(points: np.ndarray, n: int) -> np.ndarray:
    """Pick about n points evenly spaced by arc length (scale-normalised)."""
    if len(points) <= n:
        return points

    span = points.max(axis=0) - points.min(axis=0)
    span[span == 0.0] = 1.0

    scaled = points / span
    step = np.linalg.norm(np.diff(scaled, axis=0), axis=1)
    arc = np.concatenate(([0.0], np.cumsum(step)))

    targets = np.linspace(0.0, arc[-1], n)
    indices = np.unique(np.searchsorted(arc, targets).clip(0, len(points) - 1))

    return points[indices]


# =========================================================
# Binh (3)  -- 2 variables, 3 objectives, unconstrained
# =========================================================

BINH3_LOWER = [1e-6, 1e-6]
BINH3_UPPER = [1e6, 1e6]


def binh3(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [x1 - 1e6, x2 - 2e-6, x1 * x2 - 2.0]


def binh3_reference_front(n: int = 1) -> List[List[float]]:
    """All three objectives increase in both variables, so the Pareto
    front is the single ideal point at x1 = x2 = lower bound."""
    return [binh3([1e-6, 1e-6])]


# =========================================================
# Laumanns  -- 2 variables, 2 objectives, unconstrained
# =========================================================

LAUMANNS_LOWER = [-50.0, -50.0]
LAUMANNS_UPPER = [50.0, 50.0]


def laumanns(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [x1**2 + x2**2, (x1 + 2.0)**2 + x2**2]


def laumanns_reference_front(n: int = 1000) -> List[List[float]]:
    """Pareto set: segment x1 in [-2, 0], x2 = 0 (convex hull of the
    two objective minimisers)."""
    return [laumanns([t, 0.0]) for t in np.linspace(-2.0, 0.0, n)]


# =========================================================
# Murata  -- 2 variables, 2 objectives, unconstrained
# =========================================================

MURATA_LOWER = [1.0, 1.0]
MURATA_UPPER = [4.0, 2.0]


def murata(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [2.0 * math.sqrt(x1), x1 * (1.0 - x2) + 5.0]


def murata_reference_front(n: int = 1000) -> List[List[float]]:
    """f2 decreases in x2 (x1 > 0), so x2 = 2; x1 in [1, 4] is a trade-off."""
    return [murata([t, 2.0]) for t in np.linspace(1.0, 4.0, n)]


# =========================================================
# Quagliarella  -- 16 variables, 2 objectives, unconstrained
# =========================================================

QUAGLIARELLA_N_VAR = 16
QUAGLIARELLA_LOWER = [-5.12] * QUAGLIARELLA_N_VAR
QUAGLIARELLA_UPPER = [5.12] * QUAGLIARELLA_N_VAR


def _rastrigin_term(v: float) -> float:
    return v * v - 10.0 * math.cos(2.0 * math.pi * v) + 10.0


def quagliarella(x: Sequence[float]) -> List[float]:
    n = len(x)
    if n < 1:
        raise ValueError("Quagliarella requires at least 1 variable")

    return [
        math.sqrt(sum(_rastrigin_term(v) for v in x) / n),
        math.sqrt(sum(_rastrigin_term(v - 1.5) for v in x) / n),
    ]


@lru_cache(maxsize=None)
def _quagliarella_front(n_var: int, n: int, grid: int, cap: int):
    # The grid also contains the per-term minimisers 0 and 1.5 exactly.
    xs = np.unique(np.concatenate((
        np.linspace(-5.12, 5.12, grid),
        np.linspace(0.0, 1.5, 3001),
    )))
    a = xs**2 - 10.0 * np.cos(2.0 * np.pi * xs) + 10.0
    shifted = xs - 1.5
    b = shifted**2 - 10.0 * np.cos(2.0 * np.pi * shifted) + 10.0

    # Per-variable non-dominated set (a dominated value of any variable can
    # always be replaced, so only these can appear on the front).
    per_variable = _nondominated_2d(np.column_stack((a, b)))
    per_variable = _thin(per_variable, 300)

    current = per_variable

    for _ in range(n_var - 1):
        total = (
            current[:, None, :] + per_variable[None, :, :]
        ).reshape(-1, 2)

        current = _nondominated_2d(total)
        current = _thin(current, cap)

    front = np.sqrt(current / n_var)

    return tuple(map(tuple, _thin(front, n)))


def quagliarella_reference_front(
    n: int = 1000,
    n_var: int = QUAGLIARELLA_N_VAR,
    grid: int = 20001,
    cap: int = 5000,
) -> List[List[float]]:
    """Numerical front of the separable sum.

    Both objectives are monotone transforms (sqrt of a mean) of sums of
    per-variable terms, so the front is the non-dominated set of the
    n_var-fold Minkowski sum of the per-variable non-dominated set. This
    is computed by dynamic programming on a fine grid (error ~ grid spacing).
    """
    return [list(p) for p in _quagliarella_front(n_var, n, grid, cap)]


# =========================================================
# Rendon  -- 2 variables, 2 objectives, unconstrained
# =========================================================

RENDON_LOWER = [-3.0, -3.0]
RENDON_UPPER = [3.0, 3.0]


def rendon(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [
        1.0 / (x1**2 + x2**2 + 1.0),
        x1**2 + 3.0 * x2**2 + 1.0,
    ]


def rendon_reference_front(n: int = 1000) -> List[List[float]]:
    """Pareto set: x2 = 0 with x1 in [0, 3], then x1 = 3 with x2 in [0, 3]
    (symmetric copies map to the same objective values)."""
    half = n // 2
    first = [rendon([t, 0.0]) for t in np.linspace(0.0, 3.0, half)]
    second = [rendon([3.0, t]) for t in np.linspace(0.0, 3.0, n - half + 1)[1:]]
    return first + second


# =========================================================
# Rendon (2)  -- 2 variables, 2 objectives, unconstrained
# =========================================================

RENDON2_LOWER = [-3.0, -3.0]
RENDON2_UPPER = [3.0, 3.0]


def rendon2(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [x1 + x2 + 1.0, x1**2 + 2.0 * x2 - 1.0]


def rendon2_reference_front(n: int = 1000) -> List[List[float]]:
    """Both objectives increase in x2, so x2 = -3; x1 in [-3, 0] trades off."""
    return [rendon2([t, -3.0]) for t in np.linspace(-3.0, 0.0, n)]


# =========================================================
# Schaffer  -- 1 variable, 2 objectives, unconstrained
# =========================================================

SCHAFFER_LOWER = [-10.0]
SCHAFFER_UPPER = [10.0]


def schaffer(x: Sequence[float]) -> List[float]:
    (x1,) = x
    return [x1**2, (x1 - 2.0)**2]


def schaffer_reference_front(n: int = 1000) -> List[List[float]]:
    return [schaffer([t]) for t in np.linspace(0.0, 2.0, n)]


# =========================================================
# Schaffer (2)  -- 1 variable, 2 objectives, unconstrained
# =========================================================

SCHAFFER2_LOWER = [-5.0]
SCHAFFER2_UPPER = [10.0]


def schaffer2(x: Sequence[float]) -> List[float]:
    (x1,) = x

    if x1 <= 1.0:
        f1 = -x1
    elif x1 <= 3.0:
        f1 = x1 - 2.0
    elif x1 <= 4.0:
        f1 = 4.0 - x1
    else:
        f1 = x1 - 4.0

    return [f1, (x1 - 5.0)**2]


def schaffer2_reference_front(n: int = 1000) -> List[List[float]]:
    """Pareto set: x in [1, 2] and x in [4, 5]."""
    half = n // 2
    first = [schaffer2([t]) for t in np.linspace(1.0, 2.0, half)]
    second = [schaffer2([t]) for t in np.linspace(4.0, 5.0, n - half)]
    return first + second


# =========================================================
# Srinivas  -- 2 variables, 2 objectives, 2 inequality constraints
# =========================================================

SRINIVAS_LOWER = [-20.0, -20.0]
SRINIVAS_UPPER = [20.0, 20.0]


def srinivas(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [
        (x1 - 2.0)**2 + (x2 - 1.0)**2 + 2.0,
        9.0 * x1 - (x2 - 1.0)**2,
    ]


def srinivas_violation(x: Sequence[float]) -> float:
    """Sum of positive parts of g1 = x1^2 + x2^2 - 225 <= 0 and
    g2 = x1 - 3 x2 + 10 <= 0."""
    x1, x2 = x
    return (
        max(0.0, x1**2 + x2**2 - 225.0)
        + max(0.0, x1 - 3.0 * x2 + 10.0)
    )


@lru_cache(maxsize=None)
def _srinivas_front(n: int, resolution: int):
    tolerance = 1e-9

    # f1 + f2 = x1^2 + 5 x1 + 6 depends only on x1 (minimised at -2.5), so
    # the unconstrained-direction part of the Pareto set is x1 = -2.5. The
    # remaining Pareto-optimal points lie on the boundaries of the feasible
    # region: the line x1 = 3 x2 - 10 (g2) and the circle (g1).
    upper = math.sqrt(225.0 - 2.5**2)
    y = np.linspace(2.5, upper, resolution)
    interior = np.column_stack((np.full_like(y, -2.5), y))

    root = math.sqrt(60.0**2 + 4.0 * 10.0 * 125.0)
    y = np.linspace((60.0 - root) / 20.0, (60.0 + root) / 20.0, resolution)
    line = np.column_stack((3.0 * y - 10.0, y))

    t = np.linspace(0.0, 2.0 * math.pi, resolution)
    circle = np.column_stack((15.0 * np.cos(t), 15.0 * np.sin(t)))
    circle = circle[circle[:, 0] - 3.0 * circle[:, 1] + 10.0 <= tolerance]

    candidates = np.vstack((interior, line, circle))
    feasible = (
        candidates[:, 0]**2 + candidates[:, 1]**2 - 225.0 <= tolerance
    ) & (
        candidates[:, 0] - 3.0 * candidates[:, 1] + 10.0 <= tolerance
    )
    candidates = candidates[feasible]

    f1 = (candidates[:, 0] - 2.0)**2 + (candidates[:, 1] - 1.0)**2 + 2.0
    f2 = 9.0 * candidates[:, 0] - (candidates[:, 1] - 1.0)**2

    front = _nondominated_2d(np.column_stack((f1, f2)))

    return tuple(map(tuple, _thin(front, n)))


def srinivas_reference_front(
    n: int = 1000,
    resolution: int = 200001,
) -> List[List[float]]:
    """Numerical front built from the Pareto-set candidates x1 = -2.5, the
    line g2 = 0 and the circle g1 = 0 (dense parametrisation, feasibility
    filtered, ND-filtered, arc-length thinned). The result spans
    f1 in about [10.1, 225], matching the literature plot."""
    return [list(p) for p in _srinivas_front(n, resolution)]


# =========================================================
# Tanaka  -- 2 variables, 2 objectives, 2 inequality constraints
# =========================================================

TANAKA_LOWER = [0.0, 0.0]
TANAKA_UPPER = [math.pi, math.pi]


def tanaka(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [x1, x2]


def tanaka_violation(x: Sequence[float]) -> float:
    """Sum of positive parts of
    c1 = -x1^2 - x2^2 + 1 + 0.1 cos(16 atan(x1 / x2)) <= 0 and
    c2 = (x1 - 0.5)^2 + (x2 - 0.5)^2 - 0.5 <= 0."""
    x1, x2 = x
    c1 = -x1**2 - x2**2 + 1.0 + 0.1 * math.cos(16.0 * math.atan2(x1, x2))
    c2 = (x1 - 0.5)**2 + (x2 - 0.5)**2 - 0.5
    return max(0.0, c1) + max(0.0, c2)


@lru_cache(maxsize=None)
def _tanaka_front(n: int, resolution: int):
    tolerance = 1e-12

    # Boundary of c1: r(phi) = sqrt(1 + 0.1 cos(16 phi)), with
    # x1 = r sin(phi), x2 = r cos(phi) so that atan(x1 / x2) = phi.
    phi = np.linspace(0.0, math.pi / 2.0, resolution)
    r = np.sqrt(1.0 + 0.1 * np.cos(16.0 * phi))
    curve = np.column_stack((r * np.sin(phi), r * np.cos(phi)))
    inside = (
        (curve[:, 0] - 0.5)**2 + (curve[:, 1] - 0.5)**2 - 0.5 <= tolerance
    )
    curve = curve[inside]

    # Boundary of c2 (circle), keeping only points that also satisfy c1.
    theta = np.linspace(0.0, 2.0 * math.pi, resolution)
    radius = math.sqrt(0.5)
    circle = np.column_stack((
        0.5 + radius * np.cos(theta),
        0.5 + radius * np.sin(theta),
    ))
    circle = circle[(circle[:, 0] >= 0.0) & (circle[:, 1] >= 0.0)]
    c1 = (
        -circle[:, 0]**2 - circle[:, 1]**2
        + 1.0
        + 0.1 * np.cos(16.0 * np.arctan2(circle[:, 0], circle[:, 1]))
    )
    circle = circle[c1 <= tolerance]

    front = _nondominated_2d(np.vstack((curve, circle)))

    return tuple(map(tuple, _thin(front, n)))


def tanaka_reference_front(
    n: int = 1000,
    resolution: int = 400001,
) -> List[List[float]]:
    """Both objectives are the decision variables, so the front is the
    non-dominated part of the feasible region's boundary. It is computed
    by dense parametrisation of both constraint boundaries (not by random
    sampling), ND-filtered, and thinned evenly by arc length."""
    return [list(p) for p in _tanaka_front(n, resolution)]


# =========================================================
# Viennet  -- 2 variables, 3 objectives, unconstrained
# =========================================================

VIENNET_LOWER = [-2.0, -2.0]
VIENNET_UPPER = [2.0, 2.0]


def viennet(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [
        x1**2 + (x2 - 1.0)**2,
        x1**2 + (x2 + 1.0)**2 + 1.0,
        (x1 - 1.0)**2 + x2**2 + 2.0,
    ]


def _simplex_weights(divisions: int) -> np.ndarray:
    weights = [
        (i / divisions, j / divisions, (divisions - i - j) / divisions)
        for i in range(divisions + 1)
        for j in range(divisions + 1 - i)
    ]
    return np.array(weights)


def viennet_reference_front(divisions: int = 60) -> List[List[float]]:
    """Each objective is |p - c_i|^2 + const, so the Pareto set is the
    triangle with vertices c_i = (0, 1), (0, -1), (1, 0)."""
    centres = np.array([[0.0, 1.0], [0.0, -1.0], [1.0, 0.0]])
    weights = _simplex_weights(divisions)
    points = (weights[:, :, None] * centres[None, :, :]).sum(axis=1)
    return [viennet(p) for p in points]


# =========================================================
# Viennet (2)  -- 2 variables, 3 objectives, unconstrained
# =========================================================

VIENNET2_LOWER = [-4.0, -4.0]
VIENNET2_UPPER = [4.0, 4.0]


def viennet2(x: Sequence[float]) -> List[float]:
    x1, x2 = x
    return [
        (x1 - 2.0)**2 / 2.0 + (x2 + 1.0)**2 / 13.0 + 3.0,
        (x1 + x2 - 3.0)**2 / 36.0 + (-x1 + x2 + 2.0)**2 / 8.0 - 17.0,
        (x1 + 2.0 * x2 - 1.0)**2 / 175.0 + (2.0 * x2 - x1)**2 / 17.0 - 13.0,
    ]


def _quadratic_coefficients(fn, index: int):
    """Exact (H, g, c) with f_index(p) = 0.5 p^T H p + g^T p + c for a
    quadratic objective, recovered by finite differences (exact here)."""
    def f(a, b):
        return fn([a, b])[index]

    c = f(0.0, 0.0)
    g = np.array([
        (f(1.0, 0.0) - f(-1.0, 0.0)) / 2.0,
        (f(0.0, 1.0) - f(0.0, -1.0)) / 2.0,
    ])
    h11 = f(1.0, 0.0) + f(-1.0, 0.0) - 2.0 * c
    h22 = f(0.0, 1.0) + f(0.0, -1.0) - 2.0 * c
    h12 = (
        f(1.0, 1.0) - f(1.0, -1.0) - f(-1.0, 1.0) + f(-1.0, -1.0)
    ) / 4.0

    return np.array([[h11, h12], [h12, h22]]), g, c


def _minimise_box_quadratic(H, g, lower, upper):
    """Minimise 0.5 p^T H p + g^T p over a 2-D box (H positive definite)."""
    def value(p):
        return 0.5 * p @ H @ p + g @ p

    candidates = []

    p = np.linalg.solve(H, -g)
    if np.all(p >= lower) and np.all(p <= upper):
        return p

    for axis in (0, 1):
        other = 1 - axis
        for bound in (lower[axis], upper[axis]):
            # Fix coordinate `axis` at `bound`, minimise over the other.
            free = (-g[other] - H[other, axis] * bound) / H[other, other]
            q = np.zeros(2)
            q[axis] = bound
            q[other] = min(max(free, lower[other]), upper[other])
            candidates.append(q)

    return min(candidates, key=value)


def viennet2_reference_front(divisions: int = 100) -> List[List[float]]:
    """All three objectives are convex quadratics, so every Pareto-optimal
    decision vector minimises some weighted sum over the box. The weights
    are swept over a simplex grid and the images are ND-filtered."""
    forms = [_quadratic_coefficients(viennet2, i) for i in range(3)]
    lower = np.array(VIENNET2_LOWER)
    upper = np.array(VIENNET2_UPPER)

    images = []

    for w in _simplex_weights(divisions):
        H = sum(wi * form[0] for wi, form in zip(w, forms))
        g = sum(wi * form[1] for wi, form in zip(w, forms))

        if np.linalg.eigvalsh(H).min() <= 1e-12:
            continue

        p = _minimise_box_quadratic(H, g, lower, upper)
        images.append(viennet2(p))

    return _as_list(_nondominated(np.array(images)))
