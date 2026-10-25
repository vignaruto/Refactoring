def rack_beam_load_ok(load_kg: float, beam_rating_kg: float, seismic_zone: int, damaged: bool, inspection_days: int) -> tuple[bool, float]:
    seismic_factor = 1.0 if seismic_zone <= 1 else 0.85 if seismic_zone == 2 else 0.7
    derated_capacity_kg = beam_rating_kg * seismic_factor * (0.5 if damaged else 1.0)
    if damaged and inspection_days > 30 or load_kg > derated_capacity_kg or load_kg < 0.0:
        return False, round(derated_capacity_kg, 1)
    return True, round(derated_capacity_kg, 1)

if __name__ == "__main__":
    assert rack_beam_load_ok(800.0, 1000.0, 1, False, 0) == (True, 1000.0)
    assert rack_beam_load_ok(800.0, 1000.0, 3, False, 0) == (False, 700.0)
