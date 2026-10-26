def bounded_linear_solutions(a, b, c, bound):
    solutions = []
    for x in range(-bound, bound + 1):
        for y in range(-bound, bound + 1):
            if a * x + b * y == c and x >= 0 and y >= 0:
                solutions.append((x, y))
    return solutions

if __name__ == "__main__":
    assert bounded_linear_solutions(2, 3, 12, 6) == [(0, 4), (3, 2), (6, 0)]
    assert bounded_linear_solutions(2, 4, 7, 5) == []
