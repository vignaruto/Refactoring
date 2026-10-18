"""
Domain: Matrix and Grid Operations
Task: Aggregate pixel intensity values within localized neighborhood kernels.
"""

from typing import List

def aggregate_pixel_neighborhoods(grid: List[List[float]], kernel_size: int, scale_factor: float) -> List[List[float]]:
    h = len(grid)
    w = len(grid[0])
    output = [[0.0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            output[r][c] = (sum(grid[min(max(0, r + dr), h - 1)][min(max(0, c + dc), w - 1)] for dr in range(-kernel_size, kernel_size + 1) for dc in range(-kernel_size, kernel_size + 1)) * scale_factor) / float((2 * kernel_size + 1) ** 2)
    return output

if __name__ == "__main__":
    g = [[1.0, 2.0], [3.0, 4.0]]
    res = aggregate_pixel_neighborhoods(g, 1, 1.0)
    assert len(res) == 2
