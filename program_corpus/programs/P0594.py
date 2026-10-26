def double_integral_midpoint(coeffs, x_range, y_range, steps):
    a, b, c = coeffs
    (x0, x1), (y0, y1) = x_range, y_range
    hx, hy = (x1 - x0) / steps, (y1 - y0) / steps
    total = 0.0
    for i in range(steps):
        for j in range(steps):
            x, y = x0 + (i + 0.5) * hx, y0 + (j + 0.5) * hy
            cell_value = a * x * x * hx * hy + b * x * y * hx * hy + c * y * y * hx * hy
            total += cell_value
    return total

if __name__ == "__main__":
    unit = (0.0, 1.0)
    assert abs(double_integral_midpoint((1, 0, 0), unit, unit, 50) - 1 / 3) < 1e-3
    assert abs(double_integral_midpoint((0, 1, 0), unit, unit, 10) - 0.25) < 1e-9
