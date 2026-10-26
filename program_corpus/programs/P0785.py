def pitch_command(altitude, target_altitude, vertical_speed, airspeed, stall_speed=55.0):
    error = target_altitude - altitude
    command = 0.02 * error - 0.15 * vertical_speed - 0.5 * max(0.0, stall_speed * 1.2 - airspeed)
    if airspeed < stall_speed * 1.1 or altitude < 500 and error < 0 and vertical_speed < -10:
        return "recover", round(command, 2)
    return "track", round(max(-10.0, min(10.0, command)), 2)

if __name__ == "__main__":
    assert pitch_command(1000, 1500, 0, 100) == ("track", 10.0)
    assert pitch_command(400, 300, -20, 100) == ("recover", 1.0)
    assert pitch_command(3000, 3000, 0, 58) == ("recover", -4.0)
