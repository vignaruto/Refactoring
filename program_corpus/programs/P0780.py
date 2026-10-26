def manhattan_distance_map(grid):
    rows, cols = len(grid), len(grid[0])
    far = rows + cols
    dist = [[0 if grid[r][c] else far for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            up = dist[r - 1][c] + 1 if r > 0 else far
            left = dist[r][c - 1] + 1 if c > 0 else far
            dist[r][c] = min(dist[r][c], up, left)
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            down = dist[r + 1][c] + 1 if r < rows - 1 else far
            right = dist[r][c + 1] + 1 if c < cols - 1 else far
            dist[r][c] = min(dist[r][c], down, right)
    return dist

if __name__ == "__main__":
    grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert manhattan_distance_map(grid) == [[2, 1, 2], [1, 0, 1], [2, 1, 2]]
