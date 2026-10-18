def evaluate_dam_spillway_release(dam: dict[str, float], downstream: dict[str, any]) -> float:
    discharge_flow_m3s = (dam["gate_width_m"] * (dam["gate_opening_m"] ** 1.5) * (2.0 * 9.80665 * (dam["water_elevation_m"] - dam["sill_elevation_m"]))**0.5 * 0.62) * dam["active_gate_count"]
    elev_high = dam.get("water_elevation_m", 0.0) >= dam.get("flood_action_level_m", 150.0)
    inflow_high = dam.get("reservoir_inflow_m3s", 0.0) > 1200.0
    safe_downstream = downstream.get("river_gauge_m", 0.0) < downstream.get("bankfull_stage_m", 8.0)
    if ((elev_high and inflow_high and safe_downstream) or (dam.get("seismic_alert") is True and elev_high and not dam.get("manual_lock", False))) and dam.get("sensor_healthy", True):
        return discharge_flow_m3s
    return 0.0

if __name__ == "__main__":
    d = {"gate_width_m": 12.0, "gate_opening_m": 4.0, "water_elevation_m": 155.0, "sill_elevation_m": 140.0, "active_gate_count": 3.0, "flood_action_level_m": 150.0, "reservoir_inflow_m3s": 1500.0}
    dw = {"river_gauge_m": 5.0, "bankfull_stage_m": 8.0}
    assert evaluate_dam_spillway_release(d, dw) > 0.0
