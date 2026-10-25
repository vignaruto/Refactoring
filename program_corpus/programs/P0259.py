import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    return 2.0 * earth_radius_km * math.asin(math.sqrt(a))

if __name__ == "__main__":
    assert haversine_distance_km(0.0, 0.0, 0.0, 0.0) == 0.0
    assert abs(haversine_distance_km(0.0, 0.0, 0.0, 1.0) - 111.195) < 0.01
