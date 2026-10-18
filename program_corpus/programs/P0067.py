from typing import List

def transpose_matrix(matrix: List[List[float]]) -> List[List[float]]:
    rows = len(matrix)
    cols = len(matrix[0])
    transposed = []
    for c in range(cols):
        new_row = []
        for r in range(rows):
            val = matrix[r][c]
            new_row.append(val)
        transposed.append(new_row)
    return transposed

if __name__ == "__main__":
    m = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    t = transpose_matrix(m)
    assert len(t) == 3
    assert len(t[0]) == 2
