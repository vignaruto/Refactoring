def bounce_heights(drop_height, restitution, min_height=0.1, max_bounces=20):
    heights = []
    height = drop_height
    while height >= min_height and len(heights) < max_bounces and restitution < 1:
        height = round(height * restitution, 4)
        heights.append(height)
    distance = drop_height + 2 * sum(heights)
    return heights, round(distance, 4)

if __name__ == "__main__":
    heights, distance = bounce_heights(1.0, 0.5, 0.2)
    assert heights == [0.5, 0.25, 0.125]
    assert distance == 2.75
    assert bounce_heights(1.0, 1.0) == ([], 1.0)
