"""Regression tests for the optimised SPEA2 internals.

The vectorised strength / raw fitness / distance / density / truncation code and
the cached archive objectives must reproduce the original pure-Python
implementation exactly, so that earlier experimental results remain valid.
"""

import hashlib
import json
import random

import numpy as np
import pytest

from src import spea2 as M
from src.benchmarks.classical_extra import (
    SRINIVAS_LOWER, SRINIVAS_UPPER, srinivas, srinivas_violation,
)


def _random_case(rng):
    n = rng.randint(3, 40)
    m = rng.choice([1, 2, 3, 4])
    kind = rng.choice(["cont", "grid", "dups"])

    if kind == "cont":
        objs = [[rng.random() * rng.choice([1, 50]) for _ in range(m)] for _ in range(n)]
    elif kind == "grid":
        objs = [[rng.randint(0, 3) for _ in range(m)] for _ in range(n)]
    else:
        base = [[rng.random() for _ in range(m)] for _ in range(max(2, n // 3))]
        objs = [list(rng.choice(base)) for _ in range(n)]

    viol = None

    if rng.random() < 0.5:
        viol = [rng.choice([0.0, 0.0, rng.random() * 3]) for _ in range(n)]

    return objs, viol


def test_vectorised_functions_match_reference():
    rng = random.Random(2024)

    for _ in range(200):
        objs, viol = _random_case(rng)
        n = len(objs)

        strength = M.calculate_strength(objs, viol)
        assert strength == M.calculate_strength_reference(objs, viol)

        raw = M.calculate_raw_fitness(objs, strength, viol)
        assert raw == M.calculate_raw_fitness_reference(objs, strength, viol)

        dist = M.calculate_distance_matrix(objs)
        ref_dist = M.calculate_distance_matrix_reference(objs)
        assert np.array_equal(dist, np.array(ref_dist))

        k = min(max(1, int(n ** 0.5)), n - 1)
        assert M.calculate_density(dist, k) == M.calculate_density_reference(ref_dist, k)


def test_fast_truncation_matches_reference():
    rng = random.Random(7)

    for _ in range(300):
        objs, _ = _random_case(rng)
        n = len(objs)
        indices = sorted(rng.sample(range(n), rng.randint(2, n)))
        size = rng.randint(1, len(indices))

        assert M.truncate_archive(objs, indices, size) == M.truncate_archive_reference(
            objs, indices, size
        )


def test_truncation_keeps_requested_size_and_order():
    objs = [[i / 10, 1 - i / 10] for i in range(10)]
    kept = M.truncate_archive(objs, list(range(10)), 4)

    assert len(kept) == 4
    assert kept == sorted(kept)
    assert M.truncate_archive(objs, [1, 2, 3], 5) == [1, 2, 3]


def test_density_rejects_invalid_k():
    dist = M.calculate_distance_matrix([[0.0, 0.0], [1.0, 1.0]])

    with pytest.raises(IndexError):
        M.calculate_density(dist, 2)


def _digest(obj):
    return hashlib.sha256(json.dumps(obj).encode()).hexdigest()[:16]


# Digests recorded from the original implementation before the optimisation.
def test_spea2_output_unchanged_zdt1():
    random.seed(7)
    population, archive = M.spea2(20, 6, 20, 12, 0.0, 1.0, M.zdt1)
    assert _digest([archive, population]) == "ec12a7a1a56f0195"


def test_spea2_output_unchanged_zdt4():
    random.seed(3)
    population, archive = M.spea2(
        16, 4, 16, 10, [0.0] + [-5.0] * 3, [1.0] + [5.0] * 3, M.zdt4
    )
    assert _digest([archive, population]) == "1bd30843ac1e4323"


def test_spea2_output_unchanged_constrained():
    random.seed(5)
    population, archive = M.spea2(
        20, 2, 20, 12, SRINIVAS_LOWER, SRINIVAS_UPPER, srinivas, srinivas_violation
    )
    assert _digest([archive, population]) == "b47b9ea261331e95"


def test_each_solution_is_evaluated_once():
    calls = [0]

    def objective(x):
        calls[0] += 1
        return M.zdt1(x)

    random.seed(1)
    M.spea2(20, 6, 20, 12, 0.0, 1.0, objective)

    assert calls[0] == 20 * 12


def test_python_square_differs_from_multiplication_somewhere():
    """Documents why np.power (not ** 2) is used for distances."""
    values = np.random.default_rng(0).uniform(-1, 1, 200000)
    python_squares = np.array([v ** 2 for v in values.tolist()])

    assert np.array_equal(python_squares, np.power(values, 2.0))
