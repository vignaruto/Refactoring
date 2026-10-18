import math
from typing import Dict

def aerosol_settling_terminal_velocity(particle: Dict[str, float], medium_viscosity: float, gravity: float = 9.80665) -> float:
    return ((2.0 * (particle["radius_m"] ** 2) * (particle["density_kg_m3"] - particle["medium_density_kg_m3"]) * gravity) / (9.0 * medium_viscosity)) * (1.0 + (1.257 * 68e-9 / particle["radius_m"]))

if __name__ == "__main__":
    part = {"radius_m": 2.5e-6, "density_kg_m3": 1200.0, "medium_density_kg_m3": 1.2}
    assert aerosol_settling_terminal_velocity(part, 1.81e-5) > 0.0
