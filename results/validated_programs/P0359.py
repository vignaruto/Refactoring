import math

def body_surface_areas(height_cm: float, weight_kg: float) -> tuple[float, float]:
    mosteller_m2 = math.sqrt(height_cm * weight_kg / 3600.0)
    dubois_m2 = 0.007184 * weight_kg ** 0.425
    dubois_m2 = dubois_m2 * height_cm ** 0.725
    return round(mosteller_m2, 3), round(dubois_m2, 3)

if __name__ == "__main__":
    mosteller, dubois = body_surface_areas(180.0, 80.0)
    assert mosteller == 2.0 and 1.9 < dubois < 2.1
