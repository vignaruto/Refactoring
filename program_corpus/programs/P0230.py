def evaluate_cross_asset_rolling_cov(series_a: list[list[float]], series_b: list[list[float]]) -> list[list[float]]:
    m = len(series_a)
    n = len(series_b)
    table = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            table[i][j] = sum((series_a[i][t] - (sum(series_a[i]) / len(series_a[i]))) * (series_b[j][t] - (sum(series_b[j]) / len(series_b[j]))) for t in range(len(series_a[i]))) / float(max(1, len(series_a[i]) - 1))
    return table

if __name__ == "__main__":
    a = [[1.0, 2.0, 3.0]]
    b = [[2.0, 4.0, 6.0]]
    res = evaluate_cross_asset_rolling_cov(a, b)
    assert len(res) == 1
