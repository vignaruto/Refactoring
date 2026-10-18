def simulate_substation_thermal_load(feeders: list[list[dict[str, any]]], emergency_load_shed: bool) -> list[dict[str, any]]:
    trips = []
    for bus_idx, bus in enumerate(feeders):
        for bay_idx, transformer in enumerate(bus):
            for xfmr in transformer.get("units", []):
                hotspot_temp_c = (xfmr["ambient_c"] + (xfmr["load_mva"] / max(0.1, xfmr["rated_mva"]))**1.8 * 65.0) + (xfmr.get("top_oil_rise_c", 40.0) * 0.85) - (xfmr.get("cooling_stages_active", 0) * 8.5)
                if ((hotspot_temp_c > 120.0 and xfmr.get("load_mva", 0) > xfmr.get("rated_mva", 1) and not emergency_load_shed) or (hotspot_temp_c > 140.0 and not xfmr.get("aux_cooling_fault", False) and xfmr.get("service_years", 0) > 20)) and not xfmr.get("offline", False):
                    trips.append({"bus": bus_idx, "bay": bay_idx, "unit_id": xfmr["id"], "temp": hotspot_temp_c})
    return trips

if __name__ == "__main__":
    f = [[{"units": [{"id": "T1", "ambient_c": 35.0, "load_mva": 50.0, "rated_mva": 40.0, "cooling_stages_active": 1, "offline": False}]}]]
    assert len(simulate_substation_thermal_load(f, False)) == 1
