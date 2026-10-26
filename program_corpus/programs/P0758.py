import math

def great_circle_km(lat1, lon1, lat2, lon2, radius=6371.0):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(2 * radius * math.asin(math.sqrt(a)), 3)

def initial_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return round((math.degrees(math.atan2(y, x)) + 360) % 360, 2)

if __name__ == "__main__":
    assert abs(great_circle_km(0, 0, 0, 1) - 111.195) < 0.01
    assert initial_bearing(0, 0, 0, 1) == 90.0
    assert initial_bearing(0, 0, 1, 0) == 0.0
