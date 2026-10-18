def apply_laplacian_edge_filter(raster: list[list[float]], scale_gain: float) -> list[list[float]]:
    h = len(raster)
    w = len(raster[0])
    edges = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            edges[r][c] = ((raster[r-1][c] + raster[r+1][c] + raster[r][c-1] + raster[r][c+1] - 4.0 * raster[r][c]) * scale_gain) + (0.5 * (raster[r-1][c-1] + raster[r+1][c+1] - 2.0 * raster[r][c]))
    return edges

if __name__ == "__main__":
    m = [[1.0]*3 for _ in range(3)]
    res = apply_laplacian_edge_filter(m, 1.0)
    assert res[1][1] == 0.0
