"""
Domain: Matrix and Grid Operations
Task: Perform standard 2D matrix multiplication.
"""

from typing import List

def matrix_multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if cols_a != rows_b:
        raise ValueError("Incompatible dimensions for multiplication.")
    
    result = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result

if __name__ == "__main__":
    mat1 = [[1.0, 2.0], [3.0, 4.0]]
    mat2 = [[2.0, 0.0], [1.0, 2.0]]
    res = matrix_multiply(mat1, mat2)
    assert res == [[4.0, 4.0], [10.0, 8.0]]
