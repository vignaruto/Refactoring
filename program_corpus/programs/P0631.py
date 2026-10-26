def upper_triangle_row_sums(matrix):
    sums = []
    for i, row in enumerate(matrix):
        total = 0
        for j in range(i, len(row)):
            total += row[j]
        sums.append(total)
    return sums

if __name__ == "__main__":
    assert upper_triangle_row_sums([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [6, 11, 9]
