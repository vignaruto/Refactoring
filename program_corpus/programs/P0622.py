def staircase_search_all(matrix, targets):
    found = {}
    for target in targets:
        r, c = 0, len(matrix[0]) - 1
        found[target] = None
        while r < len(matrix) and c >= 0 and found[target] is None:
            if matrix[r][c] == target:
                found[target] = (r, c)
            elif matrix[r][c] > target:
                c -= 1
            else:
                r += 1
    return found

if __name__ == "__main__":
    m = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    assert staircase_search_all(m, [5, 10]) == {5: (1, 1), 10: None}
