import math

def compute_spherical_cap_geometry(radius: float, cap_height: float, density: float) -> float:
    cap_mass = density
    part = math.pi * cap_height ** 2 / 3.0
    part = part * (3.0 * radius - cap_height)
    cap_mass = cap_mass * part
    part_2 = 2.0 * math.pi * radius * cap_height * 0.05
    cap_mass = cap_mass + part_2
    return cap_mass

if __name__ == "__main__":
    assert compute_spherical_cap_geometry(10.0, 2.0, 1.5) > 0.0
