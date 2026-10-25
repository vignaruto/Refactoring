import math

def detect_insar_fringe_cells(amp: list[list[float]], phase: list[list[float]], min_amp: float) -> list[tuple[int, int, float]]:
    rows, cols = len(amp), len(amp[0])
    fringes = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            grad_x = math.atan2(math.sin(phase[r][c + 1] - phase[r][c - 1]), math.cos(phase[r][c + 1] - phase[r][c - 1]))
            grad_y = math.atan2(math.sin(phase[r + 1][c] - phase[r - 1][c]), math.cos(phase[r + 1][c] - phase[r - 1][c]))
            fringe_rate = math.hypot(grad_x, grad_y)
            if amp[r][c] >= min_amp and amp[r][c + 1] >= min_amp and fringe_rate > 1.2:
                fringes.append((r, c, round(fringe_rate, 3)))
    return fringes

if __name__ == "__main__":
    a = [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0], [5.0, 5.0, 5.0]]
    p = [[0.0, 0.0, 0.0], [0.0, 1.0, 2.5], [0.0, 0.0, 0.0]]
    assert detect_insar_fringe_cells(a, p, 2.0) == [(1, 1, 2.5)]
