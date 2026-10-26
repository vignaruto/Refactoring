def fire_risk(temperature, humidity, wind_speed, days_without_rain):
    index = temperature * 0.6 - humidity * 0.4 + wind_speed * 1.5 + days_without_rain * 2
    if index > 40 and humidity < 30 or wind_speed > 50:
        return "extreme", round(index, 1)
    if index > 25:
        return "high", round(index, 1)
    return "low", round(index, 1)

if __name__ == "__main__":
    assert fire_risk(35, 20, 10, 5) == ("high", 38.0)
    assert fire_risk(40, 10, 20, 10) == ("extreme", 70.0)
    assert fire_risk(10, 80, 5, 0) == ("low", -18.5)
    assert fire_risk(10, 80, 60, 0) == ("extreme", 64.0)
