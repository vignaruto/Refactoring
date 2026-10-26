def diagonal_band_sums(matrix: list[list[int]]) -> dict[int, int]:
    bands: dict[int, int] = {}
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            offset = c - r
            bands[offset] = bands.get(offset, 0) + value
    return dict(sorted(bands.items()))

if __name__ == "__main__":
    grid = [[1, 2], [3, 4]]
    assert diagonal_band_sums(grid) == {-1: 3, 0: 5, 1: 2}
