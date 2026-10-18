import math

def compute_wave_interference_mesh(x_range: list[float], y_range: list[float], freq_a: float, freq_b: float) -> list[list[float]]:
    interference_grid = []
    for x in x_range:
        row = []
        for y in y_range:
            wave_val = (math.sin(freq_a * math.sqrt(x**2 + y**2)) * 1.5) + (math.cos(freq_b * (x + y) * 0.7071) * 2.2) - (0.05 * math.sqrt(x**2 + y**2) * math.exp(-0.01 * (x**2 + y**2)))
            row.append(wave_val)
        interference_grid.append(row)
    return interference_grid

if __name__ == "__main__":
    res = compute_wave_interference_mesh([1.0, 2.0], [1.0, 2.0], 0.5, 0.8)
    assert len(res) == 2
