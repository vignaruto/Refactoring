def gauss_seidel_solve(a: list[list[float]], b: list[float], iterations: int) -> list[float]:
    n = len(b)
    x = [0.0] * n
    for _ in range(iterations):
        for i in range(n):
            off_diag = sum(a[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - off_diag) / a[i][i]
    return [round(val, 5) for val in x]

if __name__ == "__main__":
    sol = gauss_seidel_solve([[4.0, 1.0], [2.0, 3.0]], [1.0, 2.0], 25)
    assert sol == [0.1, 0.6]
