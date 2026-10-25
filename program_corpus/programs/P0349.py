import math

def optimize_tuned_mass_damper(freq_ratios: list[float], damping_ratios: list[float], mass_ratio: float) -> tuple[float, float, float]:
    best = (0.0, 0.0, float("inf"))
    for f_ratio in freq_ratios:
        for zeta in damping_ratios:
            if f_ratio <= 0.5 or zeta <= 0.01 or zeta >= 0.5:
                continue
            peak_amp = 0.0
            for step in range(80, 121):
                g = step / 100.0
                real_part = (f_ratio ** 2 - g ** 2) * (1.0 - g ** 2) - mass_ratio * (g ** 2) * (f_ratio ** 2)
                imag_part = 2.0 * zeta * g * f_ratio * (1.0 - g ** 2 * (1.0 + mass_ratio))
                amp = math.hypot(f_ratio ** 2 - g ** 2, 2.0 * zeta * g * f_ratio) / max(1e-9, math.hypot(real_part, imag_part))
                peak_amp = max(peak_amp, amp)
            if peak_amp < best[2]:
                best = (f_ratio, zeta, round(peak_amp, 3))
    return best

if __name__ == "__main__":
    res = optimize_tuned_mass_damper([0.95, 1.0], [0.05, 0.12], 0.05)
    assert res[0] == 0.95 and res[2] < 10.0
