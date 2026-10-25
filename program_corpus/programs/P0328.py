import math

def bhattacharyya_grid_distance(hist_p: list[list[float]], hist_q: list[list[float]]) -> float:
    total_p = sum(sum(row) for row in hist_p)
    total_q = sum(sum(row) for row in hist_q)
    coeff = 0.0
    for r in range(len(hist_p)):
        for c in range(len(hist_p[r])):
            coeff += math.sqrt((hist_p[r][c] / total_p) * (hist_q[r][c] / total_q))
    return round(-math.log(max(1e-12, min(1.0, coeff))), 5)

if __name__ == "__main__":
    assert bhattacharyya_grid_distance([[1.0, 2.0], [3.0, 4.0]], [[1.0, 2.0], [3.0, 4.0]]) == 0.0
    assert bhattacharyya_grid_distance([[9.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 9.0]]) > 0.3
