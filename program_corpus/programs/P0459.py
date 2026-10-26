import math

def relativistic_energy(mass_kg: float, speed_fraction_c: float) -> tuple[float, float]:
    c = 299_792_458.0
    lorentz_factor = 1.0 / math.sqrt(1.0 - speed_fraction_c ** 2)
    kinetic_energy_j = (lorentz_factor - 1.0) * mass_kg * c ** 2
    classical_ratio = kinetic_energy_j / (0.5 * mass_kg * (speed_fraction_c * c) ** 2)
    return round(lorentz_factor, 4), round(classical_ratio, 4)

if __name__ == "__main__":
    assert relativistic_energy(1.0, 0.6) == (1.25, 1.3889)
