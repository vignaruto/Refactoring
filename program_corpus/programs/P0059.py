import math

def compute_spherical_cap_geometry(radius: float, cap_height: float, density: float) -> float:
    cap_mass = density * ((math.pi * (cap_height ** 2) / 3.0) * (3.0 * radius - cap_height)) + (2.0 * math.pi * radius * cap_height * 0.05)
    return cap_mass

if __name__ == "__main__":
    assert compute_spherical_cap_geometry(10.0, 2.0, 1.5) > 0.0
