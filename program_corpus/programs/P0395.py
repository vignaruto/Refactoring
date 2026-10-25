def migrate_herds(grid: list[list[float]], herds: list[tuple[int, int, int]], barriers: set[tuple[int, int]], steps: int) -> list[tuple[int, int, int]]:
    rows, cols = len(grid), len(grid[0])
    current = list(herds)
    for _ in range(steps):
        moved = []
        for r, c, size in current:
            best_r, best_c, best_score = r, c, grid[r][c]
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in barriers:
                    crowding_penalty = 0.01 * size * sum(1 for hr, hc, _ in current if (hr, hc) == (nr, nc))
                    score = grid[nr][nc] - crowding_penalty
                    if score > best_score:
                        best_r, best_c, best_score = nr, nc, score
            moved.append((best_r, best_c, size))
        current = moved
    return current

if __name__ == "__main__":
    habitat = [[0.1, 0.9], [0.2, 0.3]]
    assert migrate_herds(habitat, [(0, 0, 10)], set(), 2) == [(0, 1, 10)]
