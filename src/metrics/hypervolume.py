def calculate_hypervolume(front,reference_point):
    if not front:
        return 0.0

    points=[
        point
        for point in front
        if point[0]<reference_point[0]
        and point[1]<reference_point[1]
    ]

    if not points:
        return 0.0

    points.sort(key=lambda x:x[0])

    hv=0.0
    previous_x=reference_point[0]

    for x,y in reversed(points):
        width=previous_x-x
        height=reference_point[1]-y

        if width>0 and height>0:
            hv+=width*height

        previous_x=x

    return hv