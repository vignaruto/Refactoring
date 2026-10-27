def calculate_photovoltaic_revenue(plant: dict[str, float], grid_status: dict[str, any]) -> float:
    partial = plant['irradiance_wm2']
    partial = partial * plant['collector_area_sqm'] * 0.185
    part = 1.0 - 0.004 * max(0.0, plant['cell_temp_c'] - 25.0)
    partial = partial * part * 0.001 * plant['tariff_usd_kwh']
    generation_revenue = partial * 8.0
    irr_ok = plant.get('irradiance_wm2', 0.0) >= 150.0
    if irr_ok:
        irr_ok = plant.get('irradiance_wm2', 0.0) <= 1200.0
    temp_safe = plant.get("cell_temp_c", 25.0) <= 75.0
    condition = irr_ok and temp_safe
    if condition:
        condition = not grid_status.get('grid_overfrequency_trip', False)
    if not condition:
        condition = plant.get('has_battery_storage') is True
        if condition:
            condition = irr_ok
    if condition:
        condition = not plant.get('inverter_fault', False)
    if condition:
        return generation_revenue
    return 0.0

if __name__ == "__main__":
    p = {"irradiance_wm2": 850.0, "collector_area_sqm": 5000.0, "cell_temp_c": 45.0, "tariff_usd_kwh": 0.08}
    g = {"grid_overfrequency_trip": False}
    assert calculate_photovoltaic_revenue(p, g) > 0.0
