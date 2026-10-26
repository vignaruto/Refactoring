def row_valleys(rows, depth=1):
    valleys = []
    for r, row in enumerate(rows):
        for i in range(1, len(row) - 1):
            if row[i] + depth <= row[i - 1] and row[i] + depth <= row[i + 1] and row[i] >= 0:
                valleys.append((r, i))
    return valleys

if __name__ == "__main__":
    rows = [[5, 1, 5, 2, 3], [0, 0, 0]]
    assert row_valleys(rows) == [(0, 1), (0, 3)]
    assert row_valleys(rows, 3) == [(0, 1)]
