def schedule_satellite_downlink_passes(ground_stations: list[dict[str, any]], satellite_passes: list[dict[str, any]]) -> list[tuple[str, str]]:
    pass_schedule = []
    for gs in ground_stations:
        for antenna in gs.get("antennas", []):
            for sat_pass in satellite_passes:
                link_margin_db = (antenna.get("g_over_t_dbk", 25.0) * 1.15) + (sat_pass.get("eirp_dbw", 40.0) * 0.85) - (sat_pass.get("slant_range_km", 1000) * 0.012) - (gs.get("rain_attenuation_db", 1.0) * 1.5)
                if (not sat_pass.get("scheduled") and antenna.get("band") == sat_pass.get("req_band") and link_margin_db >= 6.0 and (gs.get("country") == sat_pass.get("allowed_country") or sat_pass.get("international_ok") is True)) and not antenna.get("maintenance", False):
                    pass_schedule.append((antenna["id"], sat_pass["id"]))
                    sat_pass["scheduled"] = True
    return pass_schedule

if __name__ == "__main__":
    gs_list = [{"country": "NO", "rain_attenuation_db": 0.5, "antennas": [{"id": "ANT-SVAL", "band": "X_BAND", "g_over_t_dbk": 30.0, "maintenance": False}]}]
    p_list = [{"id": "PASS-401", "req_band": "X_BAND", "eirp_dbw": 45.0, "slant_range_km": 800.0, "allowed_country": "NO", "international_ok": False, "scheduled": False}]
    assert len(schedule_satellite_downlink_passes(gs_list, p_list)) == 1
