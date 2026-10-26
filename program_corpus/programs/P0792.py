def region_sizes(grid, min_size=2):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    sizes = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) in seen:
                continue
            value = grid[r][c]
            stack = [(r, c)]
            seen.add((r, c))
            size = 0
            while stack:
                cr, cc = stack.pop()
                size += 1
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and grid[nr][nc] == value:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            if size >= min_size:
                sizes.append((value, size))
    ordered = sorted(sizes, key=lambda s: (-s[1], str(s[0])))
    covered_percent = sum(size for _, size in sizes) * 100 / (rows * cols)
    return ordered, round(covered_percent, 1)

if __name__ == "__main__":
    grid = ["aab", "abb", "ccb"]
    ordered, covered = region_sizes(grid)
    assert ordered == [("b", 4), ("a", 3), ("c", 2)]
    assert covered == 100.0
