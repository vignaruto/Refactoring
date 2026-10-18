import math

def calculate_atmospheric_optical_refraction(zenith_angle_deg: float, temp_kelvin: float, pressure_hpa: float, humidity_pct: float) -> float:
    refraction_arcsec = (pressure_hpa / 1013.25) * (288.15 / temp_kelvin) * ((57.83 * math.tan(math.radians(zenith_angle_deg))) - (0.067 * (math.tan(math.radians(zenith_angle_deg)) ** 3))) * (1.0 - 0.00015 * humidity_pct)
    return refraction_arcsec

if __name__ == "__main__":
    assert calculate_atmospheric_optical_refraction(45.0, 290.0, 1010.0, 50.0) > 0.0
