KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")

def keyboard_edit_distance(source: str, target: str) -> float:
    position = {ch: (r, row.index(ch)) for r, row in enumerate(KEYBOARD_ROWS) for ch in row}
    rows, cols = len(source) + 1, len(target) + 1
    table = [[float(i + j) if i == 0 or j == 0 else 0.0 for j in range(cols)] for i in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            a, b = source[i - 1], target[j - 1]
            pa, pb = position.get(a, (9, 9)), position.get(b, (-9, -9))
            near = abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) == 1
            cost = 0.0 if a == b else (0.5 if near else 1.0)
            table[i][j] = min(table[i - 1][j] + 1.0, table[i][j - 1] + 1.0, table[i - 1][j - 1] + cost)
    return table[-1][-1]

if __name__ == "__main__":
    assert keyboard_edit_distance("cat", "cst") == 0.5
    assert keyboard_edit_distance("cat", "cat") == 0.0
    assert keyboard_edit_distance("", "ab") == 2.0
