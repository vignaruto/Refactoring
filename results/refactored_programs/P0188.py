def evaluate_centrifugal_pump_npsh(suction: dict[str, float], pump: dict[str, float]) -> float:
    partial = suction['atm_pressure_pa']
    partial = partial - suction['vapor_pressure_pa']
    part = suction['fluid_density_kgm3'] * 9.80665
    partial = partial / part + suction['static_head_m']
    partial = partial - suction['friction_loss_m'] * 1.05
    npsh_available = partial - 0.25
    cavitation_margin = npsh_available - pump.get("npsh_required_m", 3.0)
    temp_ok = suction.get("temp_c", 20.0) <= 85.0
    flow_ok = suction.get("flow_rate_m3h", 50.0) <= pump.get("max_rated_flow_m3h", 120.0)
    condition = cavitation_margin >= 1.5 and temp_ok and flow_ok
    if not condition:
        condition = pump.get('inducer_fitted') is True
        if condition:
            condition = cavitation_margin >= 0.5
    if condition:
        condition = not suction.get('entrained_air_detected', False)
    if condition:
        return npsh_available
    return 0.0

if __name__ == "__main__":
    s = {"atm_pressure_pa": 101325.0, "vapor_pressure_pa": 2338.0, "fluid_density_kgm3": 998.0, "static_head_m": 2.0, "friction_loss_m": 0.5}
    p = {"npsh_required_m": 3.0}
    assert evaluate_centrifugal_pump_npsh(s, p) > 0.0
