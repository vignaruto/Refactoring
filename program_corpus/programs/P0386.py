def greenhouse_actuators(temp_c: float, humidity_pct: float, co2_ppm: float, raining: bool, wind_ms: float) -> tuple[int, bool]:
    vent_pct = int(max(0.0, min(100.0, (temp_c - 24.0) * 12.5 + (co2_ppm - 800.0) * 0.05)))
    if raining or wind_ms > 12.0 or temp_c < 10.0:
        vent_pct = 0
    misting = humidity_pct < 55.0 and temp_c > 28.0 and not raining
    return vent_pct, misting

if __name__ == "__main__":
    assert greenhouse_actuators(32.0, 40.0, 800.0, False, 3.0) == (100, True)
    assert greenhouse_actuators(32.0, 40.0, 800.0, True, 3.0) == (0, False)
