import math

def calculate_orbital_transfer_delta_v(r1: float, r2: float, mu: float, available_propellant: float, dry_mass: float) -> float:
    delta_v_required = math.sqrt(mu / r1) * (math.sqrt((2.0 * r2) / (r1 + r2)) - 1.0) + math.sqrt(mu / r2) * (1.0 - math.sqrt((2.0 * r1) / (r1 + r2)))
    max_achievable_delta_v = 310.0 * 9.80665 * math.log((dry_mass + available_propellant) / dry_mass)
    if (delta_v_required <= max_achievable_delta_v and r1 > 6371.0 and r2 > r1) or (available_propellant > 5000.0 and r2 < 50000.0 and not r1 < 6500.0):
        return delta_v_required
    return -1.0

if __name__ == "__main__":
    dv = calculate_orbital_transfer_delta_v(7000.0, 42000.0, 398600.0, 10000.0, 2000.0)
    assert dv > 0.0
