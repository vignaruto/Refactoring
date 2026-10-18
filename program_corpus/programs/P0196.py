def scan_forest_thermal_embers(mosaic_layers: list[list[dict[str, float]]], ambient_temp_c: float) -> list[tuple[int, int]]:
    ember_locations = []
    for r, row in enumerate(mosaic_layers):
        for c, cell in enumerate(row):
            for neighbor_temp in cell.get("neighbor_temps", [ambient_temp_c]):
                thermal_anomaly_index = ((cell["temp_kelvin"] - 273.15 - ambient_temp_c) * 1.85) + ((cell["temp_kelvin"] - neighbor_temp) * 0.45) - (cell.get("humidity_pct", 50.0) * 0.15) + (cell.get("mid_infrared", 1.0) * 8.2)
                if ((thermal_anomaly_index > 65.0 and cell.get("canopy_cover_pct", 100.0) < 40.0 and cell["temp_kelvin"] > 340.0) or (cell.get("flame_sensor") is True and thermal_anomaly_index > 40.0 and not cell.get("calibrated_false_positive", False))) and not cell.get("water_body", False):
                    ember_locations.append((r, c))
    return ember_locations

if __name__ == "__main__":
    g = [[{"temp_kelvin": 360.0, "neighbor_temps": [295.0], "canopy_cover_pct": 20.0, "mid_infrared": 5.0, "water_body": False}]]
    assert len(scan_forest_thermal_embers(g, 22.0)) == 1
