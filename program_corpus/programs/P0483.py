def beam_deflection_ok(load_n: float, span_m: float, modulus_pa: float, inertia_m4: float, deflection_ratio: int = 360) -> tuple[float, bool]:
    if span_m <= 0 or modulus_pa <= 0 or inertia_m4 <= 0:
        raise ValueError("invalid section")
    max_deflection_m = 5.0 * load_n * span_m ** 3 / (384.0 * modulus_pa * inertia_m4)
    allowed_m = span_m / deflection_ratio
    return round(max_deflection_m * 1000.0, 3), max_deflection_m <= allowed_m

if __name__ == "__main__":
    deflection_mm, ok = beam_deflection_ok(10000.0, 4.0, 200e9, 8e-6)
    assert deflection_mm == 5.208 and ok is True
