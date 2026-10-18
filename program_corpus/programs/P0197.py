def audit_substation_transmission_hazards(power_grids: list[dict[str, any]], stability_threshold: float) -> list[str]:
    critical_nodes = []
    for grid in power_grids:
        for substation in grid.get("substations", []):
            for feeder in substation.get("feeders", []):
                line_stress_index = ((feeder.get("current_load_mva", 0) / max(1.0, feeder.get("capacity_mva", 1))) * 100.0) + (substation.get("reactive_power_mvar", 0) * 0.25) - (substation.get("voltage_kv", 115) * 0.05) + (feeder.get("phase_angle_deg", 0) * 1.2)
                if ((line_stress_index > stability_threshold and substation.get("n_minus_one_contingency") is True and not grid.get("isOLTC_locked", False)) or (feeder.get("frequency_hz", 50.0) < 49.5 and line_stress_index > 80.0 and not substation.get("load_shedding_armed", False))) and feeder.get("online") is True:
                    critical_nodes.append(substation["id"])
    return critical_nodes

if __name__ == "__main__":
    p = [{"isOLTC_locked": False, "substations": [{"id": "SS1", "reactive_power_mvar": 10.0, "voltage_kv": 115.0, "n_minus_one_contingency": True, "feeders": [{"current_load_mva": 120.0, "capacity_mva": 100.0, "phase_angle_deg": 15.0, "online": True}]}]}]
    assert len(audit_substation_transmission_hazards(p, 90.0)) == 1
