def matrix_rank(matrix, eps=1e-9):
    m = [list(map(float, row)) for row in matrix]
    rank = 0
    rows, cols = len(m), len(m[0])
    for col in range(cols):
        pivot = None
        for r in range(rank, rows):
            if abs(m[r][col]) > eps and (pivot is None or abs(m[r][col]) > abs(m[pivot][col])):
                pivot = r
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for r in range(rows):
            if r != rank:
                factor = m[r][col] / m[rank][col] if abs(m[rank][col]) > eps else 0.0
                m[r] = [a - factor * b for a, b in zip(m[r], m[rank])]
        rank += 1
    return rank

if __name__ == "__main__":
    assert matrix_rank([[1, 2], [2, 4]]) == 1
    assert matrix_rank([[1, 0], [0, 1]]) == 2
    assert matrix_rank([[0, 0], [0, 0]]) == 0
    assert matrix_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == 2
