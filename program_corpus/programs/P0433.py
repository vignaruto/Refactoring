def turbine_power_kw(wind_speed: float, rotor_diameter_m: float, air_density: float = 1.225) -> float:
    cut_in, rated_speed, cut_out = 3.0, 12.0, 25.0
    if wind_speed < cut_in or wind_speed >= cut_out or rotor_diameter_m <= 0:
        return 0.0
    swept_area = 3.141592653589793 * (rotor_diameter_m / 2.0) ** 2
    effective_speed = min(wind_speed, rated_speed)
    power_kw = 0.5 * air_density * swept_area * effective_speed ** 3 * 0.42 / 1000.0
    return round(power_kw, 1)

if __name__ == "__main__":
    assert turbine_power_kw(2.0, 100.0) == 0.0
    assert turbine_power_kw(30.0, 100.0) == 0.0
    assert turbine_power_kw(12.0, 100.0) == turbine_power_kw(15.0, 100.0) > 0
