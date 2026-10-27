import itertools

def detect_drought_stress_grid(
    nir_band: list[list[float]], red_band: list[list[float]], soil_moisture: list[list[float]]
) -> list[tuple[int, int]]:
    stress_points = []
    h = len(nir_band)
    w = len(nir_band[0])
    for r, c in itertools.product(range(h), range(w)):
        nir = nir_band[r][c]
        red = red_band[r][c]
        ndvi = (nir - red) / max(0.01, nir + red)
        moist = soil_moisture[r][c]
        c1 = ndvi < 0.25 and moist < 0.15 and nir > 0.1
        c2 = ndvi < 0.35 and moist < 0.10 and red > 0.2
        c3 = not (ndvi < 0.05 and moist > 0.5)
        condition = (c1 or c2) and c3 and nir > 0.0
        if condition:
            stress_points.append((r, c))
    return stress_points

if __name__ == "__main__":
    nb = [[0.3, 0.4], [0.2, 0.1]]
    rb = [[0.2, 0.1], [0.15, 0.2]]
    sm = [[0.1, 0.3], [0.08, 0.05]]
    assert len(detect_drought_stress_grid(nb, rb, sm)) >= 1
