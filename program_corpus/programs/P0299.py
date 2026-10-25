def search_stable_pi_gains(kp_values: list[float], ki_values: list[float], plant_gain: float, time_constant: float, dt: float, steps: int) -> list[tuple[float, float]]:
    stable = []
    for kp in kp_values:
        for ki in ki_values:
            output, integral, peak = 0.0, 0.0, 0.0
            for _ in range(steps):
                error = 1.0 - output
                integral += error * dt
                output += dt * (plant_gain * (kp * error + ki * integral) - output) / time_constant
                peak = max(peak, output)
            overshoot = max(0.0, peak - 1.0)
            if abs(1.0 - output) < 0.02 and overshoot < 0.2 and kp > 0.0:
                stable.append((kp, ki))
    return stable

if __name__ == "__main__":
    gains = search_stable_pi_gains([1.0, 2.0], [0.0, 1.0], 1.0, 1.0, 0.01, 2000)
    assert (1.0, 0.0) not in gains and (2.0, 1.0) in gains
