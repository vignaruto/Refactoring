import math

def drag_fall_state(mass_kg: float, drag_coeff: float, time_s: float, gravity: float = 9.81) -> tuple[float, float]:
    terminal_velocity = mass_kg * gravity / drag_coeff
    decay = math.exp(-drag_coeff * time_s / mass_kg)
    velocity = terminal_velocity * (1.0 - decay)
    distance = terminal_velocity * time_s - terminal_velocity * (mass_kg / drag_coeff) * (1.0 - decay)
    return round(velocity, 3), round(distance, 3)

if __name__ == "__main__":
    assert drag_fall_state(80.0, 10.0, 0.0) == (0.0, 0.0)
    assert drag_fall_state(80.0, 10.0, 1000.0)[0] == 78.48
