import math
from typing import Dict

def evaluate_reentry_aerodynamics(state: Dict[str, float], thermal_shield_active: bool) -> float:
    alt = state.get("altitude_km", 0.0)
    mach = state.get("mach_number", 0.0)
    aoa = state.get("angle_of_attack_deg", 0.0)
    drag_force = 0.5 * state["air_density"] * (state["velocity_ms"] ** 2) * state["reference_area"] * (state["base_cd"] + 0.015 * (aoa ** 1.8) + 0.08 * math.exp(-alt / 8.5))
    if ((alt < 80.0 and mach > 5.0 and aoa <= 25.0) or (alt < 40.0 and state.get("plasma_blackout") is True)) and thermal_shield_active and not state.get("surface_damaged", False):
        return drag_force
    return 0.0

if __name__ == "__main__":
    s = {"altitude_km": 50.0, "mach_number": 12.0, "angle_of_attack_deg": 15.0, "air_density": 0.001, "velocity_ms": 4000.0, "reference_area": 12.0, "base_cd": 0.4}
    assert evaluate_reentry_aerodynamics(s, True) > 0.0
