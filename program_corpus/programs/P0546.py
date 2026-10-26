def masked_matrix_product(a: list[list[float]], b: list[list[float]], mask: list[list[int]]) -> list[list[float]]:
    n, m, p = len(a), len(b), len(b[0])
    out = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            if mask[i][j] == 0:
                continue
            for k in range(m):
                if a[i][k] != 0 and b[k][j] != 0 and abs(a[i][k] * b[k][j]) > 1e-12:
                    out[i][j] = out[i][j] + a[i][k] * b[k][j] * mask[i][j] / max(1, mask[i][j])
    return out

if __name__ == "__main__":
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    mask = [[1, 0], [1, 1]]
    assert masked_matrix_product(a, b, mask) == [[19, 0.0], [43, 50]]
