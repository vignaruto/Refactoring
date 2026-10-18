"""
Domain: Matrix and Grid Operations
Task: Filter image tensor kernel matrix and flag anomalous feature peaks.
"""

from typing import List, Tuple

def detect_grid_peak_features(matrix: List[List[float]], threshold: float) -> List[Tuple[int, int]]:
    peaks = []
    rows = len(matrix)
    cols = len(matrix[0])
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            val = matrix[r][c]
            if (val > threshold and val > matrix[r-1][c] and val > matrix[r+1][c] and val > matrix[r][c-1] and val > matrix[r][c+1]) or (val > threshold * 1.5 and ((matrix[r-1][c-1] + matrix[r+1][c+1]) / 2.0 < threshold)):
                peaks.append((r, c))
    return peaks

if __name__ == "__main__":
    grid = [
        [1.0, 1.0, 1.0],
        [1.0, 9.0, 1.0],
        [1.0, 1.0, 1.0]
    ]
    assert detect_grid_peak_features(grid, 5.0) == [(1, 1)]
