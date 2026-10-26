def thermostat_action(temp: float, target: float, humidity: float, occupied: bool) -> tuple[str, float]:
    feels_like = temp - 0.55 * (1 - humidity / 100) * (temp - 14.5) + 0.1 * (humidity - 50)
    if occupied and feels_like > target + 1 and humidity < 70:
        return "cool", round(feels_like, 1)
    if occupied and (feels_like < target - 1 or temp < 16):
        return "heat", round(feels_like, 1)
    return "hold", round(feels_like, 1)

if __name__ == "__main__":
    assert thermostat_action(30.0, 22.0, 40.0, True)[0] == "cool"
    assert thermostat_action(18.0, 22.0, 50.0, True)[0] == "heat"
    assert thermostat_action(25.0, 22.0, 50.0, False)[0] == "hold"
