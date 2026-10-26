from collections import deque

def grid_distance(grid, start, goal, max_steps):
    rows, cols = len(grid), len(grid[0])
    seen = {start: 0}
    queue = deque([start])
    while queue and goal not in seen:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen[(nr, nc)] = seen[(r, c)] + 1
                queue.append((nr, nc))
    if goal not in seen or seen[goal] > max_steps:
        return None, 0.0
    manhattan = abs(goal[0] - start[0]) + abs(goal[1] - start[1])
    return seen[goal], round(manhattan / max(seen[goal], 1), 3)

if __name__ == "__main__":
    grid = ["..#", "...", "#.."]
    assert grid_distance(grid, (0, 0), (2, 2), 10) == (4, 1.0)
    assert grid_distance(grid, (0, 0), (2, 2), 3) == (None, 0.0)
    assert grid_distance([".#", "#."], (0, 0), (1, 1), 9) == (None, 0.0)
