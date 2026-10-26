def magic_square_report(m):
    target = sum(m[0])
    rows_ok = all(sum(row) == target for row in m)
    cols_ok = all(sum(col) == target for col in zip(*m))
    diag = sum(m[i][i] for i in range(len(m)))
    anti = sum(m[i][len(m) - 1 - i] for i in range(len(m)))
    if rows_ok and cols_ok and diag == target and anti == target:
        return True, target
    return False, [sum(row) for row in m] + [sum(col) for col in zip(*m)] + [diag, anti]

if __name__ == "__main__":
    assert magic_square_report([[2, 7, 6], [9, 5, 1], [4, 3, 8]]) == (True, 15)
    assert magic_square_report([[1, 2], [3, 4]]) == (False, [3, 7, 4, 6, 5, 5])
