def matrix_exponential_taylor(matrix: list[list[float]], terms: int = 12) -> list[list[float]]:
    size = len(matrix)
    result = [[float(i == j) for j in range(size)] for i in range(size)]
    term = [row[:] for row in result]
    for k in range(1, terms):
        term = [[sum(term[i][m] * matrix[m][j] for m in range(size)) / k for j in range(size)] for i in range(size)]
        for i in range(size):
            for j in range(size):
                result[i][j] += term[i][j]
    return [[round(v, 4) for v in row] for row in result]

if __name__ == "__main__":
    assert matrix_exponential_taylor([[0.0, 0.0], [0.0, 0.0]]) == [[1.0, 0.0], [0.0, 1.0]]
    assert matrix_exponential_taylor([[1.0, 0.0], [0.0, 0.0]]) == [[2.7183, 0.0], [0.0, 1.0]]
