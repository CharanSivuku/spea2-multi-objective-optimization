"""Tests for feasibility-first constraint dominance in SPEA2."""

import random

import pytest

from src.spea2 import (
    calculate_raw_fitness,
    calculate_strength,
    constraint_dominates,
    dominates,
    spea2,
    zdt1,
)


def test_feasible_dominates_infeasible_regardless_of_objectives():
    assert constraint_dominates([9.0, 9.0], 0.0, [0.0, 0.0], 0.5)
    assert not constraint_dominates([0.0, 0.0], 0.5, [9.0, 9.0], 0.0)


def test_infeasible_compared_by_violation():
    assert constraint_dominates([5.0, 5.0], 1.0, [0.0, 0.0], 2.0)
    assert not constraint_dominates([0.0, 0.0], 2.0, [5.0, 5.0], 1.0)
    # Equal violation: neither dominates.
    assert not constraint_dominates([0.0, 0.0], 1.0, [5.0, 5.0], 1.0)
    assert not constraint_dominates([5.0, 5.0], 1.0, [0.0, 0.0], 1.0)


def test_feasible_pair_uses_pareto_dominance():
    assert constraint_dominates([1.0, 1.0], 0.0, [2.0, 2.0], 0.0)
    assert not constraint_dominates([1.0, 3.0], 0.0, [2.0, 2.0], 0.0)
    assert not constraint_dominates([2.0, 2.0], 0.0, [2.0, 2.0], 0.0)


def test_all_feasible_matches_original_dominance():
    solutions = [[1.0, 4.0], [2.0, 2.0], [3.0, 1.0], [3.0, 3.0], [4.0, 4.0]]
    zeros = [0.0] * len(solutions)

    assert calculate_strength(solutions) == calculate_strength(
        solutions, zeros
    )

    strength = calculate_strength(solutions)
    assert calculate_raw_fitness(solutions, strength) == calculate_raw_fitness(
        solutions, strength, zeros
    )


def test_strength_and_raw_fitness_with_violations():
    # Solution 0 is infeasible but has the best objectives.
    solutions = [[0.0, 0.0], [5.0, 5.0], [6.0, 6.0]]
    violations = [1.0, 0.0, 0.0]

    strength = calculate_strength(solutions, violations)
    # Feasible 1 dominates infeasible 0 and feasible 2; feasible 2 also
    # dominates infeasible 0 (feasibility first).
    assert strength == [0, 2, 1]

    raw = calculate_raw_fitness(solutions, strength, violations)
    # 0 is dominated by 1 and 2 (2 + 1); 2 is dominated by 1 (2).
    assert raw == [3, 0, 2]


def test_violation_length_mismatch_rejected():
    with pytest.raises(ValueError):
        calculate_strength([[1.0, 1.0], [2.0, 2.0]], [0.0])


def test_unconstrained_spea2_unchanged_by_new_parameter():
    """constraint_function=None must reproduce the original behaviour."""
    random.seed(11)
    _, archive_default = spea2(10, 5, 10, 5, 0.0, 1.0, zdt1)

    random.seed(11)
    _, archive_none = spea2(10, 5, 10, 5, 0.0, 1.0, zdt1, None)

    assert archive_default == archive_none


def test_constraint_function_changes_selection():
    """With x[0] >= 0.5 enforced, the final archive must prefer feasible x."""
    def violation(x):
        return max(0.0, 0.5 - x[0])

    random.seed(5)
    _, archive = spea2(30, 5, 30, 20, 0.0, 1.0, zdt1, violation)

    feasible = [s for s in archive if violation(s) <= 0.0]
    assert len(feasible) >= len(archive) // 2
    assert dominates([0.0, 0.0], [1.0, 1.0])  # sanity: original helper intact
