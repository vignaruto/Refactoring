def urban_heat_hotspots(lst: list[list[float]], ndvi: list[list[float]], built_up: list[list[bool]]) -> list[tuple[int, int, float]]:
    rows, cols = len(lst), len(lst[0])
    hotspots = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            neighborhood = [lst[r + dr][c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
            anomaly = lst[r][c] - sum(neighborhood) / len(neighborhood)
            if anomaly > 2.0 and ndvi[r][c] < 0.2 and built_up[r][c]:
                hotspots.append((r, c, round(anomaly, 2)))
    return hotspots

if __name__ == "__main__":
    temps = [[30.0, 30.0, 30.0], [30.0, 40.0, 30.0], [30.0, 30.0, 30.0]]
    veg = [[0.1] * 3 for _ in range(3)]
    urban = [[True] * 3 for _ in range(3)]
    assert urban_heat_hotspots(temps, veg, urban) == [(1, 1, 10.0)]
