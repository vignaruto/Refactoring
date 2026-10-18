def extract_wetland_estuary_cells(
    dem: list[list[float]], salinity: list[list[float]], tide_limit: float
) -> list[tuple[int, int]]:
    estuary = []
    h = len(dem)
    w = len(dem[0])
    for r in range(h):
        for c in range(w):
            elev = dem[r][c]
            salt = salinity[r][c]
            c1 = elev <= tide_limit and 10.0 <= salt <= 35.0
            c2 = elev <= 0.0 and salt > 5.0 and tide_limit > 1.0
            c3 = not (elev < -10.0 and salt > 40.0)
            if (c1 or c2) and c3 and elev > -5.0:
                estuary.append((r, c))
    return estuary

if __name__ == "__main__":
    d = [[0.5, 2.0], [-1.0, 5.0]]
    s = [[25.0, 1.0], [15.0, 0.0]]
    assert len(extract_wetland_estuary_cells(d, s, 1.0)) == 2
