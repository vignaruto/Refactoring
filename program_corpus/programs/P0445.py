def flood_prone_cells(elevation: list[list[float]], rainfall: list[list[float]], drains: set[tuple[int, int]]) -> list[tuple[int, int]]:
    rows, cols = len(elevation), len(elevation[0])
    prone = []
    for r in range(rows):
        for c in range(cols):
            lower_neighbours = sum(1 for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < rows and 0 <= c + dc < cols and elevation[r + dr][c + dc] < elevation[r][c])
            if lower_neighbours == 0 and rainfall[r][c] > 50.0 and (r, c) not in drains:
                prone.append((r, c))
    return prone

if __name__ == "__main__":
    heights = [[1.0, 2.0], [2.0, 3.0]]
    rain = [[60.0, 60.0], [60.0, 60.0]]
    assert flood_prone_cells(heights, rain, set()) == [(0, 0)]
    assert flood_prone_cells(heights, rain, {(0, 0)}) == []
