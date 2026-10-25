import math

def dispersion_grid_exceedances(sources: list[dict[str, float]], receptors: list[tuple[float, float]], wind_ms: float, limit_ug_m3: float) -> list[tuple[int, float]]:
    exceeded = []
    for idx, (rx, ry) in enumerate(receptors):
        total_conc = 0.0
        for src in sources:
            dx = rx - src["x"]
            dy = ry - src["y"]
            if dx > 0.0 and wind_ms >= 0.5 and src["emission_g_s"] > 0.0:
                sigma_y = 0.08 * dx * (1.0 + 0.0001 * dx) ** (-0.5)
                sigma_z = 0.06 * dx * (1.0 + 0.0015 * dx) ** (-0.5)
                plume_ug_m3 = (src["emission_g_s"] * 1e6 / (math.pi * wind_ms * sigma_y * sigma_z)) * math.exp(-0.5 * (dy / sigma_y) ** 2 - 0.5 * (src["stack_m"] / sigma_z) ** 2)
                total_conc += plume_ug_m3
        if total_conc >= limit_ug_m3:
            exceeded.append((idx, round(total_conc, 2)))
    return exceeded

if __name__ == "__main__":
    hits = dispersion_grid_exceedances([{"x": 0.0, "y": 0.0, "stack_m": 10.0, "emission_g_s": 50.0}], [(500.0, 0.0), (-100.0, 0.0)], 4.0, 100.0)
    assert len(hits) == 1 and hits[0][0] == 0
