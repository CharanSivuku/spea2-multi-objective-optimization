"""Exact dominated hypervolume for minimization problems (any objective count)."""


def _nondominated(points):
    result = []
    for i, point in enumerate(points):
        dominated = any(
            j != i
            and all(other[k] <= point[k] for k in range(len(point)))
            and any(other[k] < point[k] for k in range(len(point)))
            for j, other in enumerate(points)
        )
        if not dominated:
            result.append(point)
    return result


def _hypervolume_recursive(points, reference_point):
    """Calculate the union volume of minimization boxes [point, reference]."""
    if not points:
        return 0.0

    dimensions = len(reference_point)
    if dimensions == 1:
        return max(0.0, reference_point[0] - min(p[0] for p in points))

    points = _nondominated(points)
    coordinates = sorted({p[0] for p in points if p[0] < reference_point[0]})
    if not coordinates:
        return 0.0

    total = 0.0
    boundaries = coordinates + [reference_point[0]]
    for index in range(len(boundaries) - 1):
        left = boundaries[index]
        right = boundaries[index + 1]
        if right <= left:
            continue
        active = [p[1:] for p in points if p[0] <= left]
        total += (right - left) * _hypervolume_recursive(
            active, reference_point[1:]
        )
    return total


def calculate_hypervolume(front, reference_point):
    """Return exact hypervolume for a minimization Pareto front.

    Points that are non-finite or not strictly better than the reference point
    in every objective are excluded. The implementation supports 1D, 2D, 3D,
    and higher-dimensional objective spaces (higher dimensions are expensive).
    """
    if not reference_point:
        raise ValueError("Reference point cannot be empty")

    dimensions = len(reference_point)
    if any(len(point) != dimensions for point in front):
        raise ValueError("Every point must match the reference-point dimension")

    valid = []
    for point in front:
        if all(
            isinstance(value, (int, float))
            and value == value
            and abs(value) != float("inf")
            for value in point
        ) and all(point[i] < reference_point[i] for i in range(dimensions)):
            valid.append(tuple(float(value) for value in point))

    if not valid:
        return 0.0

    return _hypervolume_recursive(valid, tuple(float(x) for x in reference_point))
