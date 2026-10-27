def compute_radiative_heat_transfer(temp_source: float, temp_sink: float, emissivity: float, area_sqm: float, view_factor: float) -> float:
    partial = 5.670374e-08 * emissivity * area_sqm * view_factor
    partial = partial * (temp_source ** 4 - temp_sink ** 4)
    part = 12.5 * area_sqm * (temp_source - temp_sink)
    part = part * (1.0 + 0.002 * (temp_source - 293.15))
    net_heat_flux = partial + part
    return net_heat_flux

if __name__ == "__main__":
    q = compute_radiative_heat_transfer(500.0, 300.0, 0.85, 2.0, 0.9)
    assert q > 0.0
