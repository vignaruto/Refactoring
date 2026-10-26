def asymmetric_pairs(matrix, tol):
    n = len(matrix)
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = matrix[i][j], matrix[j][i]
            if a is not None and b is not None and abs(a - b) > tol:
                bad.append((i, j))
    return bad

if __name__ == "__main__":
    m = [[1, 2, 3], [2, 1, None], [3.5, 0, 1]]
    assert asymmetric_pairs(m, 0.1) == [(0, 2)]
    assert asymmetric_pairs(m, 1.0) == []
