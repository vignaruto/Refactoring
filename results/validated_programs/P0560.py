def watering_minutes(soil_moisture: float, rain_mm: float, temp_c: float, hour: int) -> int:
    if rain_mm > 5:
        return 0
    condition = soil_moisture < 0.25 and temp_c > 30
    if condition:
        condition = not 11 <= hour <= 16
    if condition:
        return 20
    if soil_moisture < 0.35 or temp_c > 35:
        return 10
    return 0

if __name__ == "__main__":
    assert watering_minutes(0.2, 0, 32, 7) == 20
    assert watering_minutes(0.2, 0, 32, 12) == 10
    assert watering_minutes(0.5, 0, 20, 7) == 0
    assert watering_minutes(0.1, 9, 40, 7) == 0
