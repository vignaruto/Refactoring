def count_land_islands(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    seen = set()
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1 or (r, c) in seen:
                continue
            islands += 1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    inside = 0 <= nr < rows and 0 <= nc < cols
                    if inside and grid[nr][nc] == 1 and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
    return islands

if __name__ == "__main__":
    assert count_land_islands([[1, 1, 0], [0, 0, 1], [1, 0, 1]]) == 3
