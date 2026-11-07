"""Tests for the 12 classical benchmarks added in classical_extra."""

import math
import random

import numpy as np
import pytest

from experiments.benchmark_registry import build_registry
from src.benchmarks import classical_extra as c
from src.spea2 import spea2


NEW_NAMES = [
    "Binh3", "Laumanns", "Murata", "Quagliarella", "Rendon", "Rendon2",
    "Schaffer", "Schaffer2", "Srinivas", "Tanaka", "Viennet", "Viennet2",
]

# name -> (n_var, n_obj, lower, upper)
EXPECTED = {
    "Binh3": (2, 3, [1e-6, 1e-6], [1e6, 1e6]),
    "Laumanns": (2, 2, [-50.0, -50.0], [50.0, 50.0]),
    "Murata": (2, 2, [1.0, 1.0], [4.0, 2.0]),
    "Quagliarella": (16, 2, [-5.12] * 16, [5.12] * 16),
    "Rendon": (2, 2, [-3.0, -3.0], [3.0, 3.0]),
    "Rendon2": (2, 2, [-3.0, -3.0], [3.0, 3.0]),
    "Schaffer": (1, 2, [-10.0], [10.0]),
    "Schaffer2": (1, 2, [-5.0], [10.0]),
    "Srinivas": (2, 2, [-20.0, -20.0], [20.0, 20.0]),
    "Tanaka": (2, 2, [0.0, 0.0], [math.pi, math.pi]),
    "Viennet": (2, 3, [-2.0, -2.0], [2.0, 2.0]),
    "Viennet2": (2, 3, [-4.0, -4.0], [4.0, 4.0]),
}


@pytest.fixture(scope="module")
def registry():
    return build_registry()


# ---------------------------------------------------------
# Objective functions at hand-computed points
# ---------------------------------------------------------

def test_binh3_known_point():
    assert c.binh3([1e-6, 1e-6]) == pytest.approx(
        [1e-6 - 1e6, 1e-6 - 2e-6, 1e-12 - 2.0]
    )


def test_laumanns_known_points():
    assert c.laumanns([0.0, 0.0]) == [0.0, 4.0]
    assert c.laumanns([-2.0, 0.0]) == [4.0, 0.0]
    assert c.laumanns([1.0, 1.0]) == [2.0, 10.0]


def test_murata_known_points():
    assert c.murata([1.0, 2.0]) == pytest.approx([2.0, 4.0])
    assert c.murata([4.0, 2.0]) == pytest.approx([4.0, 1.0])
    assert c.murata([4.0, 1.0]) == pytest.approx([4.0, 5.0])


def test_quagliarella_known_points():
    zero = c.quagliarella([0.0] * 16)
    assert zero[0] == pytest.approx(0.0)
    # (1.5)^2 - 10 cos(3 pi) + 10 = 22.25
    assert zero[1] == pytest.approx(math.sqrt(22.25))

    shifted = c.quagliarella([1.5] * 16)
    assert shifted[0] == pytest.approx(math.sqrt(22.25))
    assert shifted[1] == pytest.approx(0.0, abs=1e-12)


def test_rendon_known_points():
    assert c.rendon([0.0, 0.0]) == [1.0, 1.0]
    assert c.rendon([3.0, 3.0]) == pytest.approx([1.0 / 19.0, 37.0])


def test_rendon2_known_points():
    assert c.rendon2([0.0, 0.0]) == [1.0, -1.0]
    assert c.rendon2([-3.0, -3.0]) == [-5.0, 2.0]


def test_schaffer_known_points():
    assert c.schaffer([0.0]) == [0.0, 4.0]
    assert c.schaffer([2.0]) == [4.0, 0.0]


@pytest.mark.parametrize("x, expected", [
    (0.0, [0.0, 25.0]),
    (-1.0, [1.0, 36.0]),
    (1.0, [-1.0, 16.0]),
    (2.0, [0.0, 9.0]),
    (3.5, [0.5, 2.25]),
    (4.0, [0.0, 1.0]),
    (5.0, [1.0, 0.0]),
])
def test_schaffer2_piecewise(x, expected):
    assert c.schaffer2([x]) == pytest.approx(expected)


def test_srinivas_known_point_and_constraints():
    assert c.srinivas([-2.5, 2.5]) == pytest.approx([24.5, -24.75])
    assert c.srinivas_violation([-2.5, 2.5]) == 0.0
    # g2 violated only: x - 3y + 10 = 0 - 0 + 10 = 10 > 0, g1 satisfied.
    assert c.srinivas_violation([0.0, 0.0]) == pytest.approx(10.0)
    # g1 violated: 20^2 + 20^2 - 225 = 575; g2: 20 - 60 + 10 < 0
    assert c.srinivas_violation([20.0, 20.0]) == pytest.approx(575.0)


def test_tanaka_feasible_and_infeasible_points():
    # Objectives are the decision variables themselves.
    assert c.tanaka([0.3, 0.4]) == [0.3, 0.4]
    # Origin is infeasible (c1 = 1.1 > 0).
    assert c.tanaka_violation([0.0, 0.0]) == pytest.approx(1.1)
    # Far outside the circle: infeasible.
    assert c.tanaka_violation([3.0, 3.0]) > 0.0
    # A point on the front is feasible.
    front_point = c.tanaka_reference_front()[10]
    assert c.tanaka_violation(front_point) <= 1e-6


def test_viennet_known_points():
    assert c.viennet([0.0, 1.0]) == [0.0, 5.0, 4.0]
    assert c.viennet([0.0, -1.0]) == [4.0, 1.0, 4.0]
    assert c.viennet([1.0, 0.0]) == [2.0, 3.0, 2.0]


def test_viennet2_known_point():
    f = c.viennet2([0.0, 0.0])
    assert f[0] == pytest.approx(2.0 + 1.0 / 13.0 + 3.0)
    assert f[1] == pytest.approx(9.0 / 36.0 + 4.0 / 8.0 - 17.0)
    assert f[2] == pytest.approx(1.0 / 175.0 - 13.0)


# ---------------------------------------------------------
# Registry: dimensions, bounds, reference fronts
# ---------------------------------------------------------

def test_registry_has_exactly_30_unique_benchmarks(registry):
    assert len(registry) == 30
    assert len(set(registry)) == 30


@pytest.mark.parametrize("name", NEW_NAMES)
def test_dimensions_and_bounds(registry, name):
    n_var, n_obj, lower, upper = EXPECTED[name]
    problem = registry[name]

    assert problem.n_var == n_var
    assert problem.n_obj == n_obj
    assert list(problem.lower) == pytest.approx(lower)
    assert list(problem.upper) == pytest.approx(upper)

    midpoint = [(lo + up) / 2.0 for lo, up in zip(problem.lower, problem.upper)]
    assert len(problem.objective(midpoint)) == n_obj


@pytest.mark.parametrize("name", NEW_NAMES)
def test_reference_front_is_finite_with_correct_dimension(registry, name):
    problem = registry[name]
    front = np.array(problem.reference_front)

    assert front.ndim == 2
    assert front.shape[1] == problem.n_obj
    assert len(front) >= 1
    assert np.isfinite(front).all()


def test_only_constrained_problems_have_constraints(registry):
    constrained = {n for n, p in registry.items() if p.constraint is not None}
    assert constrained == {"Srinivas", "Tanaka"}


@pytest.mark.parametrize("name", [
    "Laumanns", "Murata", "Rendon", "Rendon2", "Schaffer", "Schaffer2",
    "Srinivas", "Tanaka", "Viennet", "Viennet2",
])
def test_reference_front_is_mutually_nondominated(registry, name):
    front = np.array(registry[name].reference_front)

    for point in front[:: max(1, len(front) // 300)]:
        dominated = (
            np.all(front <= point, axis=1) & np.any(front < point, axis=1)
        )
        assert not dominated.any()


# ---------------------------------------------------------
# Reference fronts are not beaten by random feasible samples
# ---------------------------------------------------------

def _random_points(problem, count, rng):
    lower = np.array(problem.lower)
    upper = np.array(problem.upper)

    for _ in range(count):
        x = rng.uniform(lower, upper)

        if problem.constraint is not None and problem.constraint(x) > 0.0:
            continue

        yield problem.objective(list(x))


@pytest.mark.parametrize("name, tolerance", [
    ("Laumanns", 1e-6),
    ("Murata", 1e-6),
    ("Rendon", 1e-6),
    ("Rendon2", 1e-6),
    ("Schaffer", 1e-6),
    ("Schaffer2", 1e-6),
    ("Srinivas", 1e-6),
    ("Tanaka", 2e-3),
    ("Viennet", 1e-6),
    ("Viennet2", 1e-6),
])
def test_no_random_feasible_sample_dominates_reference_front(
    registry, name, tolerance
):
    problem = registry[name]
    front = np.array(problem.reference_front)
    rng = np.random.default_rng(12345)

    samples = np.array(list(_random_points(problem, 20000, rng)))
    assert len(samples) > 0

    # margin[k] > tolerance means some sample is better than reference
    # point k in every objective by more than the tolerance.
    for sample in samples:
        margin = np.min(front - sample, axis=1)
        assert margin.max() <= tolerance


def test_srinivas_front_matches_brute_force_grid(registry):
    """Dense feasible grid -> ND set must lie on the reference front."""
    problem = registry["Srinivas"]
    front = np.array(problem.reference_front)

    xs, ys = np.meshgrid(
        np.arange(-16.0, 4.0, 0.02), np.arange(-3.0, 16.0, 0.02)
    )
    x, y = xs.ravel(), ys.ravel()
    ok = (x**2 + y**2 <= 225.0) & (x - 3.0 * y + 10.0 <= 0.0)
    x, y = x[ok], y[ok]

    grid = np.column_stack((
        (x - 2.0)**2 + (y - 1.0)**2 + 2.0,
        9.0 * x - (y - 1.0)**2,
    ))
    brute = c._nondominated_2d(grid)

    # Every brute-force non-dominated point is close to the reference ...
    nearest = np.min(
        np.linalg.norm(brute[::20, None, :] - front[None, :, :], axis=2),
        axis=1,
    )
    assert nearest.max() < 2.0

    # ... and the reference covers the same range (guards against truncation).
    assert front[:, 0].min() == pytest.approx(brute[:, 0].min(), abs=0.5)
    # (grid discretisation lets the grid's last point sit ~1 beyond)
    assert front[:, 0].max() == pytest.approx(brute[:, 0].max(), abs=2.0)
    assert front[:, 1].min() == pytest.approx(brute[:, 1].min(), abs=1.0)


def test_quagliarella_front_not_beaten_by_samples(registry):
    problem = registry["Quagliarella"]
    front = np.array(problem.reference_front)
    rng = np.random.default_rng(7)

    samples = [
        problem.objective(list(rng.uniform(0.0, 1.5, 16)))
        for _ in range(5000)
    ] + [
        problem.objective([t] * 16) for t in np.linspace(0.0, 1.5, 1501)
    ]

    for sample in samples:
        margin = np.min(front - np.array(sample), axis=1)
        assert margin.max() <= 0.02

    # Extremes: f1 = 0 at x = 0 and f2 = 0 at x = 1.5.
    assert front[:, 0].min() == pytest.approx(0.0, abs=1e-6)
    assert front[:, 1].min() == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------
# Analytical checks
# ---------------------------------------------------------

def test_binh3_front_is_ideal_point(registry):
    front = registry["Binh3"].reference_front
    assert len(front) == 1
    assert front[0] == pytest.approx([1e-6 - 1e6, -1e-6, 1e-12 - 2.0])


def test_viennet_weighted_sum_solver_matches_triangle():
    """The generic weighted-sum minimiser used for Viennet2 must recover the
    analytical Viennet Pareto set (triangle with vertices (0,1), (0,-1),
    (1,0)) when applied to Viennet."""
    forms = [c._quadratic_coefficients(c.viennet, i) for i in range(3)]
    lower = np.array(c.VIENNET_LOWER)
    upper = np.array(c.VIENNET_UPPER)
    centres = np.array([[0.0, 1.0], [0.0, -1.0], [1.0, 0.0]])

    for w in c._simplex_weights(10):
        H = sum(wi * f[0] for wi, f in zip(w, forms))
        g = sum(wi * f[1] for wi, f in zip(w, forms))
        p = c._minimise_box_quadratic(H, g, lower, upper)

        # Equal Hessians => minimiser is the weighted centre of the triangle.
        assert p == pytest.approx(w @ centres, abs=1e-9)


def test_viennet2_quadratic_coefficients_reproduce_objectives():
    rng = np.random.default_rng(1)

    for index in range(3):
        H, g, k = c._quadratic_coefficients(c.viennet2, index)

        for _ in range(20):
            p = rng.uniform(-4.0, 4.0, 2)
            expected = c.viennet2(list(p))[index]
            actual = 0.5 * p @ H @ p + g @ p + k
            assert actual == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_box_quadratic_minimiser_respects_bounds():
    H = np.array([[2.0, 0.0], [0.0, 2.0]])
    g = np.array([-100.0, 100.0])   # unconstrained optimum far outside
    p = c._minimise_box_quadratic(
        H, g, np.array([-4.0, -4.0]), np.array([4.0, 4.0])
    )
    assert list(p) == pytest.approx([4.0, -4.0])


def test_schaffer2_front_has_expected_gap(registry):
    front = np.array(registry["Schaffer2"].reference_front)
    f1 = front[:, 0]

    assert f1.min() == pytest.approx(-1.0)
    assert f1.max() == pytest.approx(1.0)
    # Disconnected: the two pieces end at f2 = 9 and start at f2 = 1.
    assert 9.0 in np.round(front[:, 1], 6)
    assert 1.0 in np.round(front[:, 1], 6)


# ---------------------------------------------------------
# SPEA2 integration smoke tests (tiny budget)
# ---------------------------------------------------------

@pytest.mark.parametrize("name", NEW_NAMES)
def test_spea2_runs_on_each_new_benchmark(registry, name):
    problem = registry[name]
    random.seed(1)

    population, archive = spea2(
        12,
        problem.n_var,
        12,
        3,
        problem.lower,
        problem.upper,
        problem.objective,
        problem.constraint,
    )

    assert len(archive) == 12

    for solution in archive:
        assert len(solution) == problem.n_var
        assert all(
            lo <= v <= up
            for v, lo, up in zip(solution, problem.lower, problem.upper)
        )
        assert all(math.isfinite(v) for v in problem.objective(solution))


@pytest.mark.parametrize("name", ["Srinivas", "Tanaka"])
def test_constrained_spea2_finds_feasible_solutions(registry, name):
    problem = registry[name]
    random.seed(4)

    _, archive = spea2(
        40,
        problem.n_var,
        40,
        30,
        problem.lower,
        problem.upper,
        problem.objective,
        problem.constraint,
    )

    feasible = [s for s in archive if problem.constraint(s) <= 0.0]
    assert len(feasible) > 0


# ---------------------------------------------------------
# Regression tests for two reference-front errors found in existing code
# ---------------------------------------------------------

def test_deb2_reference_front_is_nondominated(registry):
    front = np.array(registry["Deb2"].reference_front)

    for point in front:
        dominated = (
            np.all(front <= point, axis=1) & np.any(front < point, axis=1)
        )
        assert not dominated.any()

    # Disconnected: several segments separated by f1 gaps (see the PDF).
    gaps = np.diff(front[:, 0]) > 0.02
    assert gaps.sum() >= 4


@pytest.mark.parametrize("name", ["DTLZ5", "DTLZ6"])
def test_dtlz56_reference_front_lies_on_true_pareto_curve(name):
    """Pareto-optimal DTLZ5/6 points (g = 0) satisfy f1 = f2 on the unit
    sphere; the reference front must too."""
    from src.benchmarks.dtlz import generate_dtlz_reference_front

    front = np.array(generate_dtlz_reference_front(name, 3, 50))

    assert np.allclose(front[:, 0], front[:, 1])
    assert np.allclose(np.linalg.norm(front, axis=1), 1.0)
