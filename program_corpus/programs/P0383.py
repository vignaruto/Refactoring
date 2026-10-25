def apparent_temperature_c(temp_c: float, wind_kmh: float, humidity_pct: float) -> float:
    if temp_c <= 10.0 and wind_kmh > 4.8 and humidity_pct >= 0.0:
        wind_chill = 13.12 + 0.6215 * temp_c - 11.37 * wind_kmh ** 0.16 + 0.3965 * temp_c * wind_kmh ** 0.16
        return round(wind_chill, 1)
    if temp_c >= 27.0 and humidity_pct >= 40.0 and humidity_pct <= 100.0:
        heat_index = temp_c + 0.5555 * (6.11 * 2.718281828 ** (5417.753 * (1 / 273.16 - 1 / (temp_c + 273.15))) * humidity_pct / 100.0 - 10.0)
        return round(heat_index, 1)
    return round(temp_c, 1)

if __name__ == "__main__":
    assert apparent_temperature_c(20.0, 10.0, 50.0) == 20.0
    assert apparent_temperature_c(0.0, 20.0, 50.0) == -5.2
    assert apparent_temperature_c(35.0, 10.0, 60.0) > 35.0
