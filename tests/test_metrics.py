import math

from src.metrics.igd import calculate_igd
from src.metrics.gd import calculate_gd
from src.metrics.hypervolume import calculate_hypervolume
from src.metrics.spacing import calculate_spacing

def test_igd_identical_fronts():
    front = [
        [0.0, 1.0],
        [0.5, 0.5],
        [1.0, 0.0]
    ]
    assert calculate_igd(front, front) == 0.0

def test_gd_identical_fronts():
    front = [
        [0.0, 1.0],
        [0.5, 0.5],
        [1.0, 0.0]
    ]
    assert calculate_gd(front, front) == 0.0

def test_igd_nonzero():
    obtained = [
        [0.0, 1.0]
    ]
    reference = [
        [0.0, 1.0],
        [1.0, 0.0]
    ]
    result = calculate_igd(obtained, reference)
    assert math.isclose(result, math.sqrt(2) / 2)

def test_gd_nonzero():
    obtained = [
        [0.0, 1.0],
        [1.0, 0.0]
    ]
    reference = [
        [0.0, 1.0]
    ]
    result = calculate_gd(obtained, reference)
    assert math.isclose(result, 1.0)

def test_hypervolume():
    front = [
        [0.5, 0.5]
    ]
    reference_point = [1.0, 1.0]
    result = calculate_hypervolume(
        front,
        reference_point
    )
    assert math.isclose(result, 0.25)

def test_spacing():
    front = [
        [0.0, 1.0],
        [0.5, 0.5],
        [1.0, 0.0]
    ]
    result = calculate_spacing(front)
    assert math.isclose(result, 0.0)