from collections import deque

def cells_within_fuel(grid: list[str], start: tuple[int, int], fuel: int) -> int:
    rows, cols = len(grid), len(grid[0])
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (r, c), used = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            inside = 0 <= nr < rows and 0 <= nc < cols
            if inside and grid[nr][nc] != "#" and (nr, nc) not in seen and used < fuel:
                seen.add((nr, nc))
                queue.append(((nr, nc), used + 1))
    return len(seen)

if __name__ == "__main__":
    assert cells_within_fuel(["..#", "...", "#.."], (0, 0), 2) == 4
