def vacuum_next_action(battery, bin_full, dirt_ahead, obstacle_ahead, docked):
    if battery < 15 and not docked:
        return "return_to_dock"
    if bin_full or battery < 15:
        return "wait"
    if dirt_ahead and not obstacle_ahead and battery >= 30:
        return "clean_forward"
    if obstacle_ahead:
        return "turn"
    return "forward"

if __name__ == "__main__":
    assert vacuum_next_action(10, False, False, False, False) == "return_to_dock"
    assert vacuum_next_action(10, False, False, False, True) == "wait"
    assert vacuum_next_action(50, False, True, False, False) == "clean_forward"
    assert vacuum_next_action(50, False, True, True, False) == "turn"
    assert vacuum_next_action(20, False, True, False, False) == "forward"
