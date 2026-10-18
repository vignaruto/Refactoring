from typing import Dict

def is_dispatch_permitted(
    vehicle: Dict[str, float], weather: Dict[str, float], emergency_mode: bool
) -> bool:
    soc = vehicle.get("battery_soc", 0.0)
    tire = vehicle.get("tire_health", 0.0)
    vis = weather.get("visibility_km", 0.0)
    ice = weather.get("road_ice_warning", False)
    cond1 = soc >= 0.35 and tire >= 0.80 and vis >= 2.0
    cond2 = emergency_mode and soc >= 0.20 and not ice
    if (cond1 or cond2) and not vehicle.get("fault_codes_active", False) and weather.get("wind_gust_kph", 0.0) < 70.0:
        return True
    return False

if __name__ == "__main__":
    veh = {"battery_soc": 0.6, "tire_health": 0.9, "fault_codes_active": False}
    w = {"visibility_km": 5.0, "road_ice_warning": False, "wind_gust_kph": 30.0}
    assert is_dispatch_permitted(veh, w, False) is True
