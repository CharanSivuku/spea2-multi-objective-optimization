"""Tests for the CEC 2020 MMO suite, its indicators and runner."""

import math
import random

import numpy as np
import pytest

from experiments.run_cec2020_mmo import run_once
from src.benchmarks.cec2020_mmo import MMO_NAMES, MMO_PROBLEMS, get_problem
from src.metrics import calculate_igd
from src.metrics.mmo import (
    cover_rate, igd, mmo_indicators, nondominated_mask,
)
from src.spea2 import spea2


# Known issue in the organisers' settings: for these two problems the hypervolume
# reference point from main.m does not cover the (local) part of the reference
# front, so those front points contribute nothing to HV.
HV_POINT_TOO_SMALL = {"MMF12_l", "MMF13_l"}


def test_hv_reference_point_issue_is_exactly_the_two_known_problems():
    offenders = {
        name for name in MMO_NAMES
        if not (MMO_PROBLEMS[name].reference_pf()
                < np.array(MMO_PROBLEMS[name].hv_reference_point)).all()
    }
    assert offenders == HV_POINT_TOO_SMALL


def test_suite_has_24_problems():
    assert len(MMO_NAMES) == 24 == len(set(MMO_NAMES))

    with pytest.raises(ValueError):
        get_problem("MMF99")


@pytest.mark.parametrize("name", MMO_NAMES)
def test_settings_are_consistent_with_reference_data(name):
    p = MMO_PROBLEMS[name]
    ps, pf = p.reference_ps(), p.reference_pf()

    assert ps.shape[1] == p.n_var == len(p.lower) == len(p.upper)
    assert pf.shape[1] == p.n_obj == len(p.hv_reference_point)
    assert len(ps) == len(pf) > 0
    assert np.isfinite(ps).all() and np.isfinite(pf).all()
    assert p.n_ops == p.n_global + p.n_local

    # protocol of the technical report: pop = 200 * N_ops, MaxFES = 10000 * N_ops
    assert p.population_size == 200 * p.n_ops
    assert p.max_evaluations == 10000 * p.n_ops
    assert p.generations == 50

    if name not in HV_POINT_TOO_SMALL:
        # the HV reference point dominates the whole reference front
        assert (pf < np.array(p.hv_reference_point)).all()


def test_n_ops_values_match_the_report_table():
    expected = {
        "MMF1": (2, 0), "MMF2": (2, 0), "MMF4": (2, 0), "MMF5": (2, 0),
        "MMF7": (2, 0), "MMF8": (2, 0), "MMF10": (1, 0), "MMF11": (1, 0),
        "MMF12": (1, 0), "MMF13": (1, 0), "MMF14": (2, 0), "MMF15": (1, 0),
        "MMF1_e": (2, 0), "MMF14_a": (2, 0), "MMF15_a": (1, 0),
        "MMF10_l": (1, 1), "MMF11_l": (1, 1), "MMF12_l": (1, 1),
        "MMF13_l": (1, 1), "MMF15_l": (1, 1), "MMF15_a_l": (1, 1),
        "MMF16_l1": (2, 1), "MMF16_l2": (1, 2), "MMF16_l3": (2, 2),
    }

    for name, (g, l) in expected.items():
        p = MMO_PROBLEMS[name]
        assert (p.n_global, p.n_local) == (g, l), name


# problems whose reference PF rows are exactly objective(reference PS rows)
ALIGNED = [
    "MMF4", "MMF10", "MMF11", "MMF12", "MMF14", "MMF15", "MMF1_e", "MMF14_a",
    "MMF15_a", "MMF10_l", "MMF11_l", "MMF12_l", "MMF15_l", "MMF15_a_l",
    "MMF16_l1", "MMF16_l2", "MMF16_l3",
]


@pytest.mark.parametrize("name", ALIGNED)
def test_objective_reproduces_reference_front_row_by_row(name):
    p = get_problem(name)
    images = np.array([p.objective(list(x)) for x in p.reference_ps()])
    assert np.abs(images - p.reference_pf()).max() < 1e-9


@pytest.mark.parametrize("name", ["MMF1", "MMF7", "MMF13", "MMF13_l"])
def test_objective_reproduces_reference_front_as_a_set(name):
    """PS rows and PF rows are not aligned here (several PSs map to one PF)."""
    p = get_problem(name)
    pf = p.reference_pf()

    for x in p.reference_ps():
        image = np.array(p.objective(list(x)))
        assert np.linalg.norm(pf - image, axis=1).min() < 1e-9


def test_mmf5_and_mmf8_lie_on_their_analytic_fronts():
    p5, p8 = get_problem("MMF5"), get_problem("MMF8")

    for x in p5.reference_ps():
        f1, f2 = p5.objective(list(x))
        assert f2 == pytest.approx(1.0 - math.sqrt(f1), abs=1e-9)

    for x in p8.reference_ps():
        f1, f2 = p8.objective(list(x))
        assert f2 == pytest.approx(math.sqrt(1.0 - f1 ** 2), abs=1e-6)


def test_mmf2_reference_ps_boundary_quirk():
    """The official code shifts x2 only when x2 > 1, so the reference point
    (0, 1) at the boundary maps off the front; every other point is on it."""
    p = get_problem("MMF2")
    pf = p.reference_pf()
    off_front = 0

    for x in p.reference_ps():
        image = np.array(p.objective(list(x)))

        if np.linalg.norm(pf - image, axis=1).min() > 1e-6:
            off_front += 1
            assert list(x) == [0.0, 1.0]

    assert off_front == 1


def test_mmf13_l_reference_set_exceeds_official_bounds():
    """Known issue in the organisers' settings (main.m marks it 'to be
    modified'): part of the local PS lies outside the declared bounds."""
    p = get_problem("MMF13_l")
    assert p.reference_ps()[:, 2].max() > p.upper[2]


def test_known_objective_values():
    assert get_problem("MMF1").objective([2.0, 0.0]) == pytest.approx([0.0, 1.0])
    assert get_problem("MMF4").objective([0.0, 0.0]) == pytest.approx([0.0, 1.0])
    # g(0.2) = 2 - exp(0) - 0.8 exp(-1); f2 = g / x1
    assert get_problem("MMF10").objective([1.0, 0.2]) == pytest.approx([1.0, 1.0 - 0.8 * math.exp(-1.0)])
    assert get_problem("MMF14").objective([0.0, 0.0, 0.25]) == pytest.approx([1.0 * 2.0, 0.0, 0.0])
    assert sum(v * v for v in get_problem("MMF14").objective([0.3, 0.6, 0.25])) == pytest.approx(4.0)


def test_mmf16_g_branches_and_domain():
    f = get_problem("MMF16_l1").objective

    # x3 < 0.5: global branch g = 2 - sin^2(4 pi x3) = 2 at x3 = 0.25 -> f = (3, 0, 0)
    assert f([0.0, 0.0, 0.25]) == pytest.approx([3.0, 0.0, 0.0])

    # x3 >= 0.5: local branch (one local peak): g = 1.328 at x3 = 0.75
    assert f([0.0, 0.0, 0.75])[0] == pytest.approx(2.328, abs=1e-3)

    with pytest.raises(ValueError):
        f([0.0, 0.0, 1.5])


# ---------------------------------------------------------------------------
# indicators
# ---------------------------------------------------------------------------

def test_igd_matches_project_igd():
    rng = np.random.default_rng(0)
    a, b = rng.random((30, 3)), rng.random((50, 3))
    assert igd(a, b) == pytest.approx(calculate_igd(a.tolist(), b.tolist()))
    assert igd(np.empty((0, 3)), b) == float("inf")


def test_cover_rate_cases():
    ref = np.array([[0.0, 0.0], [1.0, 2.0]])

    assert cover_rate(ref, ref) == pytest.approx(1.0)
    assert cover_rate(np.array([[5.0, 5.0], [6.0, 6.0]]), ref) == 0.0

    half = np.array([[0.0, 0.0], [0.5, 2.0]])
    assert cover_rate(half, ref) == pytest.approx((0.25 * 1.0) ** (1 / 4))

    # one variable ignored for the listed problems
    assert cover_rate(np.array([[0.0, 0.0], [1.0, 0.0]]), ref, "MMF10") == pytest.approx(1.0)
    assert cover_rate(np.array([[0.0, 0.0], [1.0, 0.0]]), ref, "MMF10_l") < 1.0


def test_nondominated_mask():
    pts = np.array([[1, 1], [2, 2], [0, 3], [1, 1]], dtype=float)
    assert nondominated_mask(pts).tolist() == [True, False, True, True]


def test_indicators_of_the_reference_itself():
    p = get_problem("MMF1")
    ps, pf = p.reference_ps(), p.reference_pf()
    r = mmo_indicators(ps, pf, ps, pf, p.hv_reference_point, "MMF1")

    assert r["IGDX"] == 0.0 and r["IGDF"] == 0.0
    assert r["CR"] == pytest.approx(1.0)
    assert r["HV"] > 0 and r["rHV"] == pytest.approx(1.0 / r["HV"])
    assert r["rPSP"] == 0.0     # PSP = CR / IGDX = inf


def test_indicators_get_worse_for_a_subset_of_the_reference():
    p = get_problem("MMF1")
    ps, pf = p.reference_ps(), p.reference_pf()
    half = np.arange(len(ps)) % 2 == 0
    sub = mmo_indicators(ps[half][:60], pf[half][:60], ps, pf, p.hv_reference_point, "MMF1")
    full = mmo_indicators(ps, pf, ps, pf, p.hv_reference_point, "MMF1")

    assert sub["IGDX"] > full["IGDX"] and sub["HV"] < full["HV"]


# ---------------------------------------------------------------------------
# SPEA2 on the suite (tiny budgets) and the runner
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", MMO_NAMES)
def test_spea2_runs_on_each_problem(name):
    p = get_problem(name)
    random.seed(1)
    _, archive = spea2(10, p.n_var, 10, 2, p.lower, p.upper, p.objective)

    assert len(archive) == 10

    for x in archive:
        assert all(lo <= v <= up for v, lo, up in zip(x, p.lower, p.upper))
        assert all(math.isfinite(v) for v in p.objective(x))


def test_run_once_returns_all_indicators_and_is_reproducible():
    a, b = run_once(("MMF4", 3, 3)), run_once(("MMF4", 3, 3))

    for key in ("rPSP", "rHV", "IGDX", "IGDF", "CR", "HV"):
        assert a[key] == b[key]

    assert a["evaluations"] == 400 * 3
    assert 0 < a["n_nondominated"] <= a["archive_size"] == 400
    assert a["ps"].shape[1] == 2 and a["pf"].shape[1] == 2
