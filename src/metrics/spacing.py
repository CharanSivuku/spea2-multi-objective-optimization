import math

def euclidean_distance(point_a, point_b):
    if len(point_a) != len(point_b):
        raise ValueError("Points must have the same number of objectives")
    distance = 0.0
    for a, b in zip(point_a, point_b):
        distance += (a - b) ** 2
    return math.sqrt(distance)

def calculate_spacing(front):
    if len(front) < 2:
        return 0.0
    distances = []
    for i in range(len(front)):
        minimum_distance = float("inf")
        for j in range(len(front)):
            if i == j:
                continue
            distance = euclidean_distance(
                front[i],
                front[j]
            )
            minimum_distance = min(
                minimum_distance,
                distance
            )
        distances.append(minimum_distance)
    mean_distance = sum(distances) / len(distances)
    squared_difference = 0.0
    for distance in distances:
        squared_difference += (
            distance - mean_distance
        ) ** 2
    return math.sqrt(
        squared_difference / len(distances)
    )