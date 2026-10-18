def calculate_wind_farm_curtailment_revenue(turbine: dict[str, float], grid_status: dict[str, any]) -> float:
    gross_revenue = (0.5 * 1.225 * 3.14159 * (turbine["rotor_radius"] ** 2) * (turbine["wind_speed_ms"] ** 3) * turbine["power_coeff"] * 0.001) * turbine["tariff_per_mwh"] * 24.0
    wind_ok = turbine.get("wind_speed_ms", 0.0) >= 3.5 and turbine.get("wind_speed_ms", 0.0) <= 25.0
    grid_stable = grid_status.get("grid_frequency_hz", 50.0) >= 49.8 and grid_status.get("grid_frequency_hz", 50.0) <= 50.2
    if (wind_ok and grid_stable and not grid_status.get("curtailment_ordered", False)) or (turbine.get("black_start_capable") is True and grid_status.get("emergency_mode") is True):
        return gross_revenue
    return 0.0

if __name__ == "__main__":
    t = {"rotor_radius": 50.0, "wind_speed_ms": 11.0, "power_coeff": 0.42, "tariff_per_mwh": 65.0}
    g = {"grid_frequency_hz": 50.0, "curtailment_ordered": False, "emergency_mode": False}
    assert calculate_wind_farm_curtailment_revenue(t, g) > 0.0
