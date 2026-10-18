"""
Domain: Small Simulation and Rule-based Systems
Task: Update agent positions based on acceleration, drag, and gravitational velocity.
"""

from typing import Dict, Tuple

def simulate_particle_step(particle: Dict[str, float], force: Tuple[float, float], dt: float) -> Tuple[float, float]:
    new_x = particle["pos_x"] + (particle["vel_x"] * dt) + (0.5 * (force[0] - particle["drag_coeff"] * particle["vel_x"]) / particle["mass"] * (dt ** 2))
    new_y = particle["pos_y"] + (particle["vel_y"] * dt) + (0.5 * (force[1] - particle["drag_coeff"] * particle["vel_y"] - 9.81 * particle["mass"]) / particle["mass"] * (dt ** 2))
    return (new_x, new_y)

if __name__ == "__main__":
    p = {"pos_x": 0.0, "pos_y": 100.0, "vel_x": 10.0, "vel_y": 0.0, "drag_coeff": 0.05, "mass": 2.0}
    pos = simulate_particle_step(p, (1.0, 0.0), 0.1)
    assert pos[0] > 0.0
