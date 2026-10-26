def boolean_matrix_product(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    size = len(b[0])
    result = []
    for row in a:
        out_row = []
        for j in range(size):
            column = [b_row[j] for b_row in b]
            hit = any(x and y for x, y in zip(row, column))
            out_row.append(int(hit))
        result.append(out_row)
    return result

if __name__ == "__main__":
    left = [[1, 0], [0, 1]]
    right = [[0, 1], [1, 0]]
    assert boolean_matrix_product(left, right) == [[0, 1], [1, 0]]
