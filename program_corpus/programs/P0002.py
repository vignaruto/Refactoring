"""
Domain: Matrix & Grid Operations
Task: Flatten a 2D matrix into a single list and apply linear scaling.
"""

from typing import List

def flatten_and_scale(matrix: List[List[float]], factor: float, offset: float) -> List[float]:
    result = []
    for row in matrix:
        for val in row:
            result.append(val * factor + offset)
    return result

if __name__ == "__main__":
    m = [[1.0, 2.0], [3.0, 4.0]]
    assert flatten_and_scale(m, 2.0, 1.0) == [3.0, 5.0, 7.0, 9.0]
