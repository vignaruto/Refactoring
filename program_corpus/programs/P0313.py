import math

def rc_thermal_step(ambient_c: float, initial_c: float, power_w: float, thermal_res_cw: float, thermal_cap_jc: float, elapsed_s: float) -> float:
    tau = thermal_res_cw * thermal_cap_jc
    steady_state_c = ambient_c + power_w * thermal_res_cw
    instantaneous_c = steady_state_c + (initial_c - steady_state_c) * math.exp(-elapsed_s / tau)
    return round(instantaneous_c, 3)

if __name__ == "__main__":
    assert rc_thermal_step(25.0, 25.0, 10.0, 2.0, 5.0, 0.0) == 25.0
    assert rc_thermal_step(25.0, 25.0, 10.0, 2.0, 5.0, 1000.0) == 45.0
