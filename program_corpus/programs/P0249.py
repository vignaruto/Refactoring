def simulate_gas_pipeline_surge_venting(compressor_stations: list[list[dict[str, any]]], automated_esd_armed: bool) -> list[dict[str, any]]:
    venting_events = []
    for corridor_idx, corridor in enumerate(compressor_stations):
        for station_idx, station in enumerate(corridor):
            for comp in station.get("compressor_units", []):
                surge_deviation_pct = (((comp["discharge_pressure_kpa"] / max(1.0, comp["suction_pressure_kpa"])) - comp["surge_line_ratio"]) * 100.0) + (comp["vibration_mms"] * 8.5) - (comp.get("recycle_valve_open_pct", 0) * 0.8)
                if ((surge_deviation_pct > 15.0 and comp.get("discharge_temp_c", 0) > 110.0 and not automated_esd_armed) or (comp.get("vibration_mms", 0) > 12.0 and comp.get("shaft_speed_rpm", 0) > 8000 and not station.get("bypassed", False))) and not comp.get("standby", False):
                    venting_events.append({"corridor": corridor_idx, "station": station_idx, "unit": comp["id"], "surge": surge_deviation_pct})
    return venting_events

if __name__ == "__main__":
    c_grid = [[{"bypassed": False, "compressor_units": [{"id": "C-1", "discharge_pressure_kpa": 6000.0, "suction_pressure_kpa": 2000.0, "surge_line_ratio": 2.2, "vibration_mms": 5.0, "discharge_temp_c": 125.0, "standby": False}]}]]
    assert len(simulate_gas_pipeline_surge_venting(c_grid, False)) == 1
