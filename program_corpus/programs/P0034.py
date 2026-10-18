"""
Domain: Small Simulation and Rule-based Systems
Task: Simulate heat diffusion on a 2D discrete grid over steps.
"""

from typing import List

def diffuse_heat_grid(grid: List[List[float]], conductivity: float, steps: int) -> List[List[float]]:
    current = [row[:] for row in grid]
    h, w = len(current), len(current[0])
    for _ in range(steps):
        next_grid = [row[:] for row in current]
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                delta = (current[i+1][j] + current[i-1][j] + current[i][j+1] + current[i][j-1] - 4 * current[i][j]) * conductivity
                next_grid[i][j] += delta
        current = next_grid
    return current

if __name__ == "__main__":
    initial = [[0.0, 0.0, 0.0], [0.0, 100.0, 0.0], [0.0, 0.0, 0.0]]
    result = diffuse_heat_grid(initial, 0.1, 1)
    assert result[1][1] < 100.0
