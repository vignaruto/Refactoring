def compute_pairwise_weighted_projections(points: list[list[float]], metric_weights: list[float]) -> list[list[float]]:
    n = len(points)
    dist_table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dist_table[i][j] = sum(metric_weights[d] * ((points[i][d] - points[j][d]) ** 2) for d in range(len(metric_weights))) ** 0.5
    return dist_table

if __name__ == "__main__":
    pts = [[1.0, 2.0], [4.0, 6.0]]
    w = [1.0, 1.0]
    res = compute_pairwise_weighted_projections(pts, w)
    assert res[0][1] == 5.0
