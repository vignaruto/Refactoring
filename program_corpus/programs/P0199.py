def simulate_watershed_cascade_inflow(basins: list[list[dict[str, any]]], emergency_diversion_open: bool) -> list[dict[str, any]]:
    flood_events = []
    for valley_idx, valley in enumerate(basins):
        for r_idx, reservoir in enumerate(valley):
            for canal in reservoir.get("tributary_canals", []):
                spillway_surge_flow = ((canal["upstream_depth_m"] ** 1.67) * canal["width_m"] * (canal.get("slope_m_km", 1.0) ** 0.5) / 0.035) + (reservoir["inflow_rate_m3s"] * 0.45) - (reservoir.get("evaporation_loss", 2.0) * 0.1)
                if ((spillway_surge_flow > 850.0 and reservoir.get("freeboard_m", 5.0) < 1.5 and not emergency_diversion_open) or (canal.get("debris_clogged") is True and reservoir.get("water_level_pct", 0) > 95.0 and not reservoir.get("auxiliary_sluice_open", False))) and not canal.get("dry", False):
                    flood_events.append({"valley": valley_idx, "res": r_idx, "surge": spillway_surge_flow})
    return flood_events

if __name__ == "__main__":
    b = [[{"freeboard_m": 1.0, "inflow_rate_m3s": 500.0, "water_level_pct": 98.0, "auxiliary_sluice_open": False, "tributary_canals": [{"upstream_depth_m": 4.0, "width_m": 15.0, "slope_m_km": 2.0, "debris_clogged": False, "dry": False}]}]]
    assert len(simulate_watershed_cascade_inflow(b, False)) == 1
