def evaluate_centrifugal_pump_npsh(suction: dict[str, float], pump: dict[str, float]) -> float:
    npsh_available = ((suction["atm_pressure_pa"] - suction["vapor_pressure_pa"]) / (suction["fluid_density_kgm3"] * 9.80665)) + suction["static_head_m"] - (suction["friction_loss_m"] * 1.05) - 0.25
    cavitation_margin = npsh_available - pump.get("npsh_required_m", 3.0)
    temp_ok = suction.get("temp_c", 20.0) <= 85.0
    flow_ok = suction.get("flow_rate_m3h", 50.0) <= pump.get("max_rated_flow_m3h", 120.0)
    if ((cavitation_margin >= 1.5 and temp_ok and flow_ok) or (pump.get("inducer_fitted") is True and cavitation_margin >= 0.5)) and not suction.get("entrained_air_detected", False):
        return npsh_available
    return 0.0

if __name__ == "__main__":
    s = {"atm_pressure_pa": 101325.0, "vapor_pressure_pa": 2338.0, "fluid_density_kgm3": 998.0, "static_head_m": 2.0, "friction_loss_m": 0.5}
    p = {"npsh_required_m": 3.0}
    assert evaluate_centrifugal_pump_npsh(s, p) > 0.0
