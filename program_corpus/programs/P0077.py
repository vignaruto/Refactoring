from typing import List

def bilinear_grid_interpolation(grid: List[List[float]], x_coords: List[float], y_coords: List[float]) -> List[List[float]]:
    output = []
    for x in x_coords:
        row = []
        for y in y_coords:
            x1, y1 = int(x), int(y)
            x2, y2 = min(x1 + 1, len(grid) - 1), min(y1 + 1, len(grid[0]) - 1)
            val = (grid[x1][y1] * (x2 - x) * (y2 - y)) + (grid[x2][y1] * (x - x1) * (y2 - y)) + (grid[x1][y2] * (x2 - x) * (y - y1)) + (grid[x2][y2] * (x - x1) * (y - y1))
            row.append(val)
        output.append(row)
    return output

if __name__ == "__main__":
    g = [[1.0, 2.0], [3.0, 4.0]]
    res = bilinear_grid_interpolation(g, [0.5], [0.5])
    assert len(res) == 1
