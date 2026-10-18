def calculate_photovoltaic_revenue(plant: dict[str, float], grid_status: dict[str, any]) -> float:
    generation_revenue = (plant["irradiance_wm2"] * plant["collector_area_sqm"] * 0.185 * (1.0 - 0.004 * max(0.0, plant["cell_temp_c"] - 25.0)) * 0.001) * plant["tariff_usd_kwh"] * 8.0
    irr_ok = plant.get("irradiance_wm2", 0.0) >= 150.0 and plant.get("irradiance_wm2", 0.0) <= 1200.0
    temp_safe = plant.get("cell_temp_c", 25.0) <= 75.0
    if ((irr_ok and temp_safe and not grid_status.get("grid_overfrequency_trip", False)) or (plant.get("has_battery_storage") is True and irr_ok)) and not plant.get("inverter_fault", False):
        return generation_revenue
    return 0.0

if __name__ == "__main__":
    p = {"irradiance_wm2": 850.0, "collector_area_sqm": 5000.0, "cell_temp_c": 45.0, "tariff_usd_kwh": 0.08}
    g = {"grid_overfrequency_trip": False}
    assert calculate_photovoltaic_revenue(p, g) > 0.0
