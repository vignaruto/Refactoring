import math

def quadrant_integral(func, bounds, steps, radius, exact=0.0):
    (x0, x1), (y0, y1) = bounds
    dx = (x1 - x0) / steps
    dy = (y1 - y0) / steps
    r2 = radius * radius
    total = 0.0
    for i in range(steps):
        x = x0 + (i + 0.5) * dx
        for j in range(steps):
            y = y0 + (j + 0.5) * dy
            if x * x + y * y <= r2 and x >= 0 and y >= 0:
                total += func(x, y) * dx * dy
    return round(total, 4), round(abs(total - exact) / exact * 100, 2) if exact else 0.0

if __name__ == "__main__":
    bounds = ((-1.0, 1.0), (-1.0, 1.0))
    exact = math.pi / 4
    unit = lambda x, y: 1.0
    result = quadrant_integral(unit, bounds, 200, 1.0, exact)
    area, err = result
    assert abs(area - exact) < 0.01
    assert err < 1
