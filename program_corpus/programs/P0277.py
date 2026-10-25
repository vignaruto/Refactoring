def shifted_point(point: list[float], i: int, di: int, j: int, dj: int, step: float) -> list[float]:
    moved = list(point)
    moved[i] += di * step
    moved[j] += dj * step
    return moved

def numerical_hessian(func, point: list[float], step: float = 1e-4) -> list[list[float]]:
    n = len(point)
    hessian = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            hessian[i][j] = (func(shifted_point(point, i, 1, j, 1, step)) - func(shifted_point(point, i, 1, j, -1, step)) - func(shifted_point(point, i, -1, j, 1, step)) + func(shifted_point(point, i, -1, j, -1, step))) / (4.0 * step * step)
    return hessian

if __name__ == "__main__":
    h = numerical_hessian(lambda v: v[0] ** 2 + 3.0 * v[0] * v[1] + 2.0 * v[1] ** 2, [0.5, -1.0])
    assert all(abs(h[r][c] - [[2.0, 3.0], [3.0, 4.0]][r][c]) < 1e-3 for r in range(2) for c in range(2))
