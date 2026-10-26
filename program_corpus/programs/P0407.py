def thermostat_hysteresis(readings: list[float], low: float, high: float) -> list[bool]:
    heating = False
    states = []
    for temp in readings:
        if temp < low:
            heating = True
        elif temp > high:
            heating = False
        states.append(heating)
    return states

if __name__ == "__main__":
    temps = [18.0, 19.5, 21.5, 20.0, 18.5]
    assert thermostat_hysteresis(temps, 19.0, 21.0) == [True, True, False, False, True]
