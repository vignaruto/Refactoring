def fast_charge_current_amps(soc: float, temp_c: float, cell_v: float, capacity_ah: float, fault_flag: bool) -> float:
    if fault_flag or temp_c < 0.0 or temp_c > 55.0 or cell_v >= 4.25 or soc >= 1.0:
        return 0.0
    base_c_rate = 2.0 if 15.0 <= temp_c <= 40.0 and soc < 0.5 else 1.0
    voltage_taper = max(0.1, (4.20 - max(3.60, cell_v)) / 0.60)
    commanded_amps = capacity_ah * base_c_rate * min(1.0, voltage_taper) * (1.0 - 0.5 * max(0.0, soc - 0.8) / 0.2)
    return round(commanded_amps, 3)

if __name__ == "__main__":
    assert fast_charge_current_amps(0.3, 25.0, 3.6, 50.0, False) == 100.0
    assert fast_charge_current_amps(0.3, -5.0, 3.6, 50.0, False) == 0.0
