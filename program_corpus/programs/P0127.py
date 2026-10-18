import math

def compute_2d_dft_real(spatial_matrix: list[list[float]]) -> list[list[float]]:
    m = len(spatial_matrix)
    n = len(spatial_matrix[0])
    output = [[0.0] * n for _ in range(m)]
    for u in range(m):
        for v in range(n):
            output[u][v] = sum(spatial_matrix[x][y] * math.cos(2.0 * math.pi * ((float(u * x) / float(m)) + (float(v * y) / float(n)))) for x in range(m) for y in range(n))
    return output

if __name__ == "__main__":
    mat = [[1.0, 0.0], [0.0, 1.0]]
    res = compute_2d_dft_real(mat)
    assert len(res) == 2
