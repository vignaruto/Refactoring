import math

def saturation_and_dew_point(temp_c: float, rel_humidity_pct: float) -> tuple[float, float]:
    sat_kpa = 0.61078
    sat_kpa = sat_kpa * math.exp(17.27 * temp_c / (temp_c + 237.3))
    actual_kpa = sat_kpa * (rel_humidity_pct / 100.0)
    gamma = math.log(actual_kpa / 0.61078)
    dew_point_c = (237.3 * gamma) / (17.27 - gamma)
    return round(sat_kpa, 4), round(dew_point_c, 2)

if __name__ == "__main__":
    sat, dew = saturation_and_dew_point(25.0, 50.0)
    assert abs(sat - 3.1678) < 0.01 and abs(dew - 13.86) < 0.1
