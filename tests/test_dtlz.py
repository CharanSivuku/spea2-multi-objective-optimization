import math
import pytest

from src.benchmarks.dtlz import (
    dtlz1, dtlz2, dtlz3, dtlz4, dtlz5, dtlz6, dtlz7,
    generate_dtlz_reference_front,
)


@pytest.mark.parametrize("fn", [dtlz1, dtlz2, dtlz3, dtlz4, dtlz5, dtlz6, dtlz7])
def test_dtlz_returns_three_finite_objectives(fn):
    result = fn([0.5] * 12)
    assert len(result) == 3
    assert all(math.isfinite(v) for v in result)


def test_dtlz1_global_front_is_half_simplex():
    assert dtlz1([0.5] * 12) == pytest.approx([0.125, 0.125, 0.25])
    assert sum(generate_dtlz_reference_front("DTLZ1", 3, 8)[0]) == pytest.approx(0.5)


def test_dtlz2_global_front_is_unit_sphere():
    result = dtlz2([0.5] * 12)
    assert sum(v * v for v in result) == pytest.approx(1.0)


def test_dtlz3_global_front_is_unit_sphere():
    result = dtlz3([0.5] * 12)
    assert sum(v * v for v in result) == pytest.approx(1.0)


def test_dtlz7_reference_front_is_three_dimensional():
    front = generate_dtlz_reference_front("DTLZ7", 3, 25)
    assert front
    assert all(len(point) == 3 for point in front)


def test_invalid_dtlz_input_rejected():
    with pytest.raises(ValueError):
        dtlz2([0.5])
