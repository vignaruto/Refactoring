def elevator_dispatch_action(floor: int, target: int, load_kg: float, max_kg: float, fire_alarm: bool, door_blocked: bool) -> str:
    if fire_alarm and floor != 1 and not door_blocked:
        return "RECALL_GROUND"
    if door_blocked or load_kg > max_kg:
        return "HOLD_ALARM"
    if fire_alarm and floor == 1:
        return "PARK_OPEN"
    if target > floor and load_kg <= max_kg:
        return "ASCEND"
    if target < floor and load_kg <= max_kg:
        return "DESCEND"
    return "IDLE"

if __name__ == "__main__":
    assert elevator_dispatch_action(5, 8, 300.0, 800.0, True, False) == "RECALL_GROUND"
    assert elevator_dispatch_action(3, 7, 900.0, 800.0, False, False) == "HOLD_ALARM"
    assert elevator_dispatch_action(2, 6, 400.0, 800.0, False, False) == "ASCEND"
