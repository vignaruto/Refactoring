import math

def rbf_surface_interpolation(grid_x: list[float], grid_y: list[float], centers: list[tuple[float, float, float]], epsilon: float) -> list[list[float]]:
    surface = []
    for x in grid_x:
        row = []
        for y in grid_y:
            height = sum(w * math.sqrt(1.0 + (epsilon**2) * ((x - cx)**2 + (y - cy)**2)) for cx, cy, w in centers) + (0.01 * (x**2 + y**2))
            row.append(height)
        surface.append(row)
    return surface

if __name__ == "__main__":
    c = [(0.0, 0.0, 1.0), (1.0, 1.0, 2.0)]
    res = rbf_surface_interpolation([0.5], [0.5], c, 0.5)
    assert len(res) == 1
