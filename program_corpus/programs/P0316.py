def pascal_triangle_table(order: int) -> list[list[int]]:
    rows = []
    for r in range(order + 1):
        row = [1] * (r + 1)
        for c in range(1, r):
            row[c] = rows[r - 1][c - 1] + rows[r - 1][c]
        rows.append(row)
    return rows

if __name__ == "__main__":
    assert pascal_triangle_table(4)[-1] == [1, 4, 6, 4, 1]
    assert pascal_triangle_table(0) == [[1]]
