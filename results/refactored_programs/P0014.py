"""
Domain: Matrix and Grid Operations
Task: Compute pairwise Euclidean distances across a set of points.
"""

import itertools

import math
from typing import List, Tuple

def compute_distance_matrix(points: List[Tuple[float, float]]) -> List[List[float]]:
    n = len(points)
    dist_matrix = [[0.0] * n for _ in range(n)]
    for i, j in itertools.product(range(n), range(n)):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        dist_matrix[i][j] = math.sqrt(dx * dx + dy * dy)
    return dist_matrix

if __name__ == "__main__":
    pts = [(0.0, 0.0), (3.0, 4.0)]
    matrix = compute_distance_matrix(pts)
    assert matrix[0][1] == 5.0
