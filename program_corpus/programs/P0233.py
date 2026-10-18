import math

def calculate_doppler_acoustic_frequency(source_freq: float, temp_c: float, wind_ms: float, observer_vel: float, source_vel: float) -> float:
    shifted_frequency = source_freq * ((331.3 * math.sqrt(1.0 + temp_c / 273.15) + wind_ms - observer_vel) / (331.3 * math.sqrt(1.0 + temp_c / 273.15) + wind_ms - source_vel)) * (1.0 - 0.0015 * abs(wind_ms))
    valid_speeds = abs(source_vel) < 300.0 and abs(observer_vel) < 300.0
    valid_temp = temp_c >= -50.0 and temp_c <= 60.0
    if ((valid_speeds and valid_temp and source_freq > 20.0) or (abs(wind_ms) < 5.0 and valid_temp)) and not source_freq > 20000.0:
        return shifted_frequency
    return 0.0

if __name__ == "__main__":
    f = calculate_doppler_acoustic_frequency(1000.0, 20.0, 5.0, 0.0, 25.0)
    assert f > 1000.0
