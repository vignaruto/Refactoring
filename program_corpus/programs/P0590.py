def kron_expand(a, b):
    rows_b, cols_b = len(b), len(b[0])
    width = len(a[0]) * cols_b
    height = len(a) * rows_b
    out = [[0] * width for _ in range(height)]
    for i, row in enumerate(a):
        for j, x in enumerate(row):
            for p in range(rows_b):
                for q in range(cols_b):
                    out[i * rows_b + p][j * cols_b + q] = x * b[p][q]
    return out

if __name__ == "__main__":
    swap = [[0, 1], [1, 0]]
    assert kron_expand([[1, 2]], swap) == [[0, 1, 0, 2], [1, 0, 2, 0]]
