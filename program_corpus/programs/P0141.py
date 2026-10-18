def detect_perilous_escarpments(
    elevation: list[list[float]], critical_drop: float
) -> list[tuple[int, int]]:
    hazards = []
    h = len(elevation)
    w = len(elevation[0])
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            curr = elevation[r][c]
            drop_north = curr - elevation[r-1][c]
            drop_south = curr - elevation[r+1][c]
            cond_a = drop_north > critical_drop and drop_south > critical_drop
            cond_b = drop_north > critical_drop * 1.5 and curr > 500.0
            cond_c = not (drop_north == drop_south and curr < 100.0)
            if (cond_a or cond_b) and cond_c and drop_north > 0.0:
                hazards.append((r, c))
    return hazards

if __name__ == "__main__":
    grid = [[10.0, 10.0, 10.0], [10.0, 80.0, 10.0], [10.0, 10.0, 10.0]]
    assert len(detect_perilous_escarpments(grid, 30.0)) == 1
