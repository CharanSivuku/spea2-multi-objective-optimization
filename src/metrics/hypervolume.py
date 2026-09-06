def calculate_hypervolume(front, reference_point):
    if not front:
        return 0.0
    if len(reference_point) != 2:
        raise ValueError(
            "This implementation supports exactly 2 objectives"
        )
    sorted_front = sorted(front, key=lambda point: point[0])
    hypervolume = 0.0
    previous_x = reference_point[0]
    for point in reversed(sorted_front):
        x = point[0]
        y = point[1]
        width = previous_x - x
        height = reference_point[1] - y
        if width > 0 and height > 0:
            hypervolume += width * height
        previous_x = x
    return hypervolume