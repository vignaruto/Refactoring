def dock_detention_charge(arrival_min: int, release_min: int, free_minutes: int, hourly_rate: float, carrier_late: bool, appointment_kept: bool, weather_delay_min: int) -> float:
    if carrier_late or not appointment_kept or release_min <= arrival_min:
        return 0.0
    billable_minutes = max(0, release_min - arrival_min - free_minutes - weather_delay_min)
    tiered_charge = min(billable_minutes, 120) / 60.0 * hourly_rate + max(0, billable_minutes - 120) / 60.0 * hourly_rate * 1.5
    return round(tiered_charge, 2)

if __name__ == "__main__":
    assert dock_detention_charge(0, 300, 120, 60.0, False, True, 0) == 210.0
    assert dock_detention_charge(0, 300, 120, 60.0, True, True, 0) == 0.0
