def min_vertical_seam(energy: list[list[float]], protected: set[tuple[int, int]], penalty: float) -> tuple[float, list[int]]:
    rows, cols = len(energy), len(energy[0])
    cost = [row[:] for row in energy]
    for r in range(1, rows):
        for c in range(cols):
            candidates = [cost[r - 1][k] for k in (c - 1, c, c + 1) if 0 <= k < cols]
            cost[r][c] += min(candidates)
            if c == 0 or c == cols - 1 or (r, c) in protected:
                cost[r][c] += penalty
    seam = [min(range(cols), key=lambda k: cost[-1][k])]
    for r in range(rows - 2, -1, -1):
        prev = seam[-1]
        options = [k for k in (prev - 1, prev, prev + 1) if 0 <= k < cols]
        seam.append(min(options, key=lambda k: cost[r][k]))
    return cost[-1][seam[0]], seam[::-1]

if __name__ == "__main__":
    energy = [[1, 5, 1], [5, 1, 5], [1, 5, 1]]
    assert min_vertical_seam(energy, set(), 0.0) == (3, [0, 1, 0])
