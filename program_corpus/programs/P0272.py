def classify_triangle(a: float, b: float, c: float) -> str:
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"
    if a + b <= c or a + c <= b or b + c <= a:
        return "degenerate"
    if a == b and b == c:
        return "equilateral"
    if a == b or b == c or a == c:
        return "isosceles"
    return "scalene"

if __name__ == "__main__":
    assert classify_triangle(3, 4, 5) == "scalene"
    assert classify_triangle(2, 2, 2) == "equilateral"
    assert classify_triangle(2, 2, 3) == "isosceles"
    assert classify_triangle(1, 2, 3) == "degenerate"
    assert classify_triangle(0, 2, 3) == "invalid"
