def poly_multiply(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result

def poly_at(coeffs, x):
    total = 0
    for power, c in enumerate(coeffs):
        total += c * x ** power
    return total

def slope_at(c, x, h=1e-3):
    slope = (8 * poly_at(c, x + h) - 8 * poly_at(c, x - h) - poly_at(c, x + 2 * h) + poly_at(c, x - 2 * h)) / (12 * h)
    return slope

if __name__ == "__main__":
    assert poly_multiply([1, 1], [1, -1]) == [1, 0, -1]
    assert abs(slope_at([0, 0, 1], 3.0) - 6.0) < 1e-6
