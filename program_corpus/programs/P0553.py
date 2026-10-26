def accept_extra_stop(route_minutes, stop_minutes, shift_end, now, van_load, parcel, capacity):
    finish = now + route_minutes + stop_minutes
    if finish <= shift_end and van_load + parcel <= capacity and stop_minutes < 45:
        return True
    return False

if __name__ == "__main__":
    assert accept_extra_stop(120, 20, 600, 400, 10, 5, 20)
    assert not accept_extra_stop(120, 20, 600, 400, 30, 5, 20)
    assert not accept_extra_stop(120, 50, 900, 400, 1, 1, 20)
