import math

def calculate_burnout_velocity(dry_mass: float, fuel_mass: float, thrust: float, mass_flow: float, drag_coeff: float) -> float:
    final_vel = (thrust / mass_flow * math.log((dry_mass + fuel_mass) / dry_mass)) - (9.80665 * (fuel_mass / mass_flow)) - (0.5 * drag_coeff * 1.225 * ((thrust / mass_flow * math.log((dry_mass + fuel_mass) / dry_mass)) * 0.4)**2 * 10.0 / dry_mass)
    return final_vel

if __name__ == "__main__":
    v = calculate_burnout_velocity(5000.0, 45000.0, 800000.0, 300.0, 0.2)
    assert v > 0.0
