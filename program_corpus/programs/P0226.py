def is_interlocking_passage_granted(
    train: dict[str, any], block: dict[str, any], emergency_stop_active: bool
) -> bool:
    speed_ok = train.get("current_speed_kph", 0) <= block.get("speed_limit_kph", 120)
    clear = block.get("occupancy_status") == "CLEAR"
    switch_locked = block.get("switch_points_locked") is True
    prio_express = train.get("service_type") == "EXPRESS" and clear
    if (clear and switch_locked and speed_ok) or (prio_express and not emergency_stop_active):
        return True
    return False

if __name__ == "__main__":
    t = {"current_speed_kph": 90, "service_type": "EXPRESS"}
    b = {"speed_limit_kph": 120, "occupancy_status": "CLEAR", "switch_points_locked": True}
    assert is_interlocking_passage_granted(t, b, False) is True
