import math

def snell_refraction_deg(incident_deg: float, c_medium1: float, c_medium2: float) -> tuple[str, float]:
    if incident_deg < 0.0 or incident_deg >= 90.0 or c_medium1 <= 0.0 or c_medium2 <= 0.0:
        raise ValueError("invalid angle or wave speeds")
    sin_transmitted = (c_medium2 / c_medium1) * math.sin(math.radians(incident_deg))
    if sin_transmitted >= 1.0:
        critical_deg = math.degrees(math.asin(c_medium1 / c_medium2))
        return ("total_internal_reflection", round(critical_deg, 3))
    transmitted_deg = math.degrees(math.asin(sin_transmitted))
    return ("refracted", round(transmitted_deg, 3))

if __name__ == "__main__":
    assert snell_refraction_deg(30.0, 1500.0, 1500.0) == ("refracted", 30.0)
    assert snell_refraction_deg(60.0, 1500.0, 3000.0) == ("total_internal_reflection", 30.0)
