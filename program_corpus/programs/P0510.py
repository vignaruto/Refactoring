def choose_elevator_direction(floor: int, requests: list[int], moving_up: bool) -> str:
    above = [r for r in requests if r > floor]
    below = [r for r in requests if r < floor]
    if not requests:
        return "idle"
    if moving_up and above or not below and above:
        return "up"
    if below:
        return "down"
    return "open"

if __name__ == "__main__":
    assert choose_elevator_direction(3, [5, 1], True) == "up"
    assert choose_elevator_direction(3, [5, 1], False) == "down"
    assert choose_elevator_direction(3, [1], True) == "down"
    assert choose_elevator_direction(3, [3], True) == "open"
    assert choose_elevator_direction(3, [], True) == "idle"
