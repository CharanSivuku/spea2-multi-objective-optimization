import math

def euclidean_distance(point_a, point_b):
    if len(point_a) != len(point_b):
        raise ValueError("Points must have the same number of objectives")
    distance = 0.0
    for a, b in zip(point_a, point_b):
        distance += (a - b) ** 2

    return math.sqrt(distance)


def calculate_igd(obtained_front, reference_front):
    if not reference_front:
        raise ValueError("Reference front cannot be empty")
    if not obtained_front:
        return float("inf")
    total_distance = 0.0
    for reference_point in reference_front:
        minimum_distance = float("inf")
        for obtained_point in obtained_front:
            distance = euclidean_distance(
                reference_point,
                obtained_point
            )
            minimum_distance = min(
                minimum_distance,
                distance
            )
        total_distance += minimum_distance
    return total_distance / len(reference_front)