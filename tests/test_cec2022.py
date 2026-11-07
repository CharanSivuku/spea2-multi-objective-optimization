"""Tests for the CEC 2022 single-objective suite and its runner."""

import hashlib
import math
import random
from pathlib import Path

import numpy as np
import pytest

from experiments.run_cec2022 import FESTracker, TARGET_ERROR, run_once
from src.benchmarks import cec2022 as C
from src.benchmarks.cec2022 import CEC2022Function, F_STAR, load_seeds, run_seed

ALL = [(f, d) for d in (10, 20) for f in range(1, 13)]


@pytest.fixture(scope="module")
def functions():
    return {(f, d): CEC2022Function(f, d) for f, d in ALL}


def test_official_data_files_are_unmodified():
    """Every data file must match the checksum recorded when it was copied."""
    listing = (C.DATA_DIR / "SHA256SUMS.txt").read_text().splitlines()
    assert len(listing) == 43

    for line in listing:
        digest, name = line.split()
        assert hashlib.sha256((C.DATA_DIR / name).read_bytes()).hexdigest() == digest, name


@pytest.mark.parametrize("func, dim", ALL)
def test_global_optimum_value(functions, func, dim):
    f = functions[(func, dim)]
    assert f.error(f.optimum) == pytest.approx(0.0, abs=1e-8)
    assert f(f.optimum) == pytest.approx(F_STAR[func], abs=1e-8)


@pytest.mark.parametrize("func, dim", ALL)
def test_optimum_is_not_beaten_by_random_points(functions, func, dim):
    f = functions[(func, dim)]
    rng = random.Random(func * 100 + dim)

    for _ in range(30):
        x = [rng.uniform(-100, 100) for _ in range(dim)]
        value = f(x)
        assert math.isfinite(value)
        assert value >= F_STAR[func] - 1e-6


@pytest.mark.parametrize("func, dim", ALL)
def test_error_grows_away_from_optimum(functions, func, dim):
    f = functions[(func, dim)]
    o = np.array(f.optimum)
    far = (o + 50.0 * np.sign(np.array(range(1, dim + 1)) - dim / 2 - 0.5)).clip(-100, 100)
    assert f.error(far.tolist()) > 1e-3


def test_function_interface_and_validation(functions):
    f = functions[(1, 10)]

    assert f.lower == -100.0 and f.upper == 100.0
    assert f.objective(f.optimum) == [F_STAR[1]]

    with pytest.raises(ValueError):
        f([0.0] * 9)

    with pytest.raises(ValueError):
        CEC2022Function(13, 10)

    with pytest.raises(ValueError):
        CEC2022Function(1, 15)


def test_zakharov_matches_independent_formula(functions):
    f = functions[(1, 10)]
    data = C._Data(1, 10)
    rng = np.random.default_rng(1)

    for _ in range(5):
        x = rng.uniform(-100, 100, 10)
        z = data.M @ (x - data.shift)
        s2 = 0.5 * np.dot(np.arange(1, 11), z)
        expected = np.sum(z ** 2) + s2 ** 2 + s2 ** 4 + 300.0
        assert f(x.tolist()) == pytest.approx(expected, rel=1e-9)


def test_rosenbrock_matches_independent_formula(functions):
    f = functions[(2, 10)]
    data = C._Data(2, 10)
    rng = np.random.default_rng(2)

    for _ in range(5):
        x = rng.uniform(-100, 100, 10)
        z = data.M @ ((x - data.shift) * 2.048 / 100.0) + 1.0
        expected = np.sum(100.0 * (z[:-1] ** 2 - z[1:]) ** 2 + (z[:-1] - 1.0) ** 2) + 400.0
        assert f(x.tolist()) == pytest.approx(expected, rel=1e-9)


def test_f3_official_quirk_rotation_has_no_effect(functions):
    """The C reference computes F3 from the un-rotated shifted vector."""
    f = functions[(3, 10)]
    data = C._Data(3, 10)
    rng = np.random.default_rng(3)

    for _ in range(5):
        x = rng.uniform(-100, 100, 10)
        y = x - data.shift
        pair = np.sqrt(y[:-1] ** 2 + y[1:] ** 2)
        total = np.sum(np.sqrt(pair) + np.sqrt(pair) * np.sin(50.0 * pair ** 0.2) ** 2)
        expected = total ** 2 / 81.0 + 600.0
        assert f(x.tolist()) == pytest.approx(expected, rel=1e-9)


def test_f4_is_rotated_rastrigin(functions):
    f = functions[(4, 10)]
    data = C._Data(4, 10)
    rng = np.random.default_rng(4)

    for _ in range(5):
        x = rng.uniform(-100, 100, 10)
        z = data.M @ ((x - data.shift) * 5.12 / 100.0)
        expected = np.sum(z ** 2 - 10.0 * np.cos(2 * np.pi * z) + 10.0) + 800.0
        assert f(x.tolist()) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("proportions, dim, expected", [
    ([0.4, 0.4, 0.2], 10, [4, 4, 2]),
    ([0.4, 0.4, 0.2], 20, [8, 8, 4]),
    ([0.1, 0.2, 0.2, 0.2, 0.1, 0.2], 10, [1, 2, 2, 2, 1, 2]),
    ([0.1, 0.2, 0.2, 0.2, 0.1, 0.2], 20, [2, 4, 4, 4, 2, 4]),
    ([0.3, 0.2, 0.2, 0.1, 0.2], 10, [3, 2, 2, 1, 2]),
    ([0.3, 0.2, 0.2, 0.1, 0.2], 20, [6, 4, 4, 2, 4]),
])
def test_hybrid_group_sizes(proportions, dim, expected):
    sizes = C._group_sizes(proportions, dim)
    assert sizes == expected and sum(sizes) == dim


@pytest.mark.parametrize("dim", [10, 20])
def test_shuffle_is_a_permutation(dim):
    for func in (6, 7, 8):
        shuffle = C._Data(func, dim).shuffle
        assert sorted(shuffle.tolist()) == list(range(1, dim + 1))


def test_composition_weights_prefer_nearest_component(functions):
    """Near the first component's optimum the composition equals component 0."""
    f = functions[(9, 10)]
    o = np.array(f.optimum)
    value = f(o + 1e-9)
    assert value == pytest.approx(F_STAR[9], abs=1e-3)


def test_seed_file_and_seed_rule():
    seeds = load_seeds()
    assert seeds.shape == (1000,)

    # seed_ind = (D/10 * f * runs + run_id) - runs, 0-based after mod 1000
    assert run_seed(10, 1, 1) == int(seeds[1])
    assert run_seed(20, 12, 30) == int(seeds[(2 * 12 * 30 + 30 - 30) % 1000])
    assert len({run_seed(10, 3, r) for r in range(1, 31)}) > 25


# ---------------------------------------------------------------------------
# runner: evaluation budget, checkpoints, termination
# ---------------------------------------------------------------------------

def test_checkpoints_follow_the_report_formula():
    f = CEC2022Function(1, 10)
    tracker = FESTracker(f, 200_000)

    assert tracker.checkpoints[0] == 200
    assert tracker.checkpoints[-1] == 200_000
    assert tracker.checkpoints == sorted(tracker.checkpoints)
    assert tracker.checkpoints[5] == math.floor(10 ** (5 / 5 - 3) * 200_000)


def test_tracker_stops_at_target_error():
    f = CEC2022Function(1, 10)
    tracker = FESTracker(f, 1000)

    with pytest.raises(Exception):
        tracker(f.optimum)

    assert tracker.fe_term == 1
    assert tracker.column() == [TARGET_ERROR] * 16 + [1]


def test_tracker_counts_every_evaluation_and_records_best_so_far():
    f = CEC2022Function(1, 10)
    tracker = FESTracker(f, 500)
    rng = random.Random(0)
    best = float("inf")

    with pytest.raises(Exception):
        while True:
            x = [rng.uniform(-100, 100) for _ in range(10)]
            best = min(best, f.error(x))
            tracker(x)

    assert tracker.fes == 500
    assert tracker.fe_term == 500
    column = tracker.column()
    assert len(column) == 17
    assert column[15] == pytest.approx(best)
    assert all(a >= b for a, b in zip(column[:15], column[1:16]))


def test_run_once_respects_budget_and_is_reproducible():
    job = (5, 10, 1, 30, 20, 20, 400)
    a, b = run_once(job), run_once(job)

    assert a["fe_term"] == 400
    assert a["final_error"] == b["final_error"]
    assert a["seed"] == run_seed(10, 5, 1)
    assert len(a["column"]) == 17
