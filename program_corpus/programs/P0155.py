def matrix_diagonal_metrics(grid: list[list[float]]) -> dict[str, float]:
    n = len(grid)
    main_trace = 0.0
    anti_trace = 0.0
    for idx in range(n):
        main_trace += grid[idx][idx]
        anti_trace += grid[idx][n - 1 - idx]
    return {
        "main_trace": main_trace,
        "anti_trace": anti_trace,
        "diff": abs(main_trace - anti_trace)
    }

if __name__ == "__main__":
    mat = [[1.0, 2.0], [3.0, 4.0]]
    res = matrix_diagonal_metrics(mat)
    assert res["main_trace"] == 5.0
