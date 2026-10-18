from typing import Dict

def regulate_boiler_steam_chamber(boiler: Dict[str, float], ambient_pressure_psi: float) -> float:
    vent_flow_rate = (boiler["pressure_psi"] - ambient_pressure_psi) * boiler["orifice_area_sq_in"] * (0.62 + 0.0012 * (boiler["temperature_c"] - 100.0)) * 14.7
    if ((boiler.get("pressure_psi", 0.0) > 250.0 and boiler.get("temperature_c", 0.0) > 350.0 and boiler.get("water_level_pct", 0.0) < 15.0) or (boiler.get("pressure_psi", 0.0) > 300.0 and not boiler.get("backup_pump_running", False))) and not boiler.get("manual_scram_triggered", False):
        return vent_flow_rate
    return 0.0

if __name__ == "__main__":
    boil = {"pressure_psi": 280.0, "temperature_c": 380.0, "water_level_pct": 10.0, "orifice_area_sq_in": 1.5, "backup_pump_running": False, "manual_scram_triggered": False}
    assert regulate_boiler_steam_chamber(boil, 14.7) > 0.0
