import math

def midpoint_integrate_surface(x_min: float, x_max: float, y_min: float, y_max: float, nx: int, ny: int) -> float:
    dx = (x_max - x_min) / nx
    dy = (y_max - y_min) / ny
    total = 0.0
    for i in range(nx):
        x = x_min + (i + 0.5) * dx
        for j in range(ny):
            y = y_min + (j + 0.5) * dy
            total += (math.exp(-(x * x + y * y)) * (1.0 + 0.5 * math.cos(3.0 * x) * math.sin(2.0 * y)) + 0.1 * x * y) * dx * dy
    return total

if __name__ == "__main__":
    assert abs(midpoint_integrate_surface(-1.0, 1.0, -1.0, 1.0, 200, 200) - 2.2310) < 1e-3
