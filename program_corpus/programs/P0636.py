def pascal_mod_rows(rows, modulus):
    table = [[1]]
    for n in range(1, rows):
        prev = table[-1]
        row = [1]
        for k in range(1, n):
            row.append((prev[k - 1] + prev[k]) % modulus)
        row.append(1)
        table.append(row)
    return table

if __name__ == "__main__":
    table = pascal_mod_rows(5, 3)
    assert table[3] == [1, 0, 0, 1]
    assert table[4] == [1, 1, 0, 1, 1]
