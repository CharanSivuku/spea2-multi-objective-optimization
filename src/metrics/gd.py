import math

def euclidean_distance(point_a, point_b):
    if len(point_a) != len(point_b):
        raise ValueError("Points must have the same number of objectives")
    distance = 0.0
    for a, b in zip(point_a, point_b):
        distance += (a - b) ** 2
    return math.sqrt(distance)

def calculate_gd(obtained_front, reference_front):
    if not obtained_front:
        return float("inf")
    if not reference_front:
        raise ValueError("Reference front cannot be empty")
    total_squared_distance = 0.0
    for obtained_point in obtained_front:
        minimum_distance = float("inf")
        for reference_point in reference_front:
            distance = euclidean_distance(
                obtained_point,
                reference_point
            )
            minimum_distance = min(
                minimum_distance,
                distance
            )
        total_squared_distance += minimum_distance ** 2
    return math.sqrt(
        total_squared_distance / len(obtained_front)
    )