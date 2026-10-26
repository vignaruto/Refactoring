def thermostat_states(temps, low=18.0, high=22.0):
    heating = False
    states = []
    for temp in temps:
        if temp < low:
            heating = True
        elif temp > high:
            heating = False
        states.append("on" if heating else "off")
    return states

if __name__ == "__main__":
    temps = [17, 19, 21, 23, 20, 17.5]
    expected = ["on", "on", "on", "off", "off", "on"]
    assert thermostat_states(temps) == expected
