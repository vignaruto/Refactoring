def next_signal_phase(phase: str, elapsed_s: int, ped_button: bool, emergency: bool, queue_len: int) -> str:
    if emergency:
        return "ALL_RED"
    if phase == "GREEN" and (elapsed_s >= 45 or (ped_button and elapsed_s >= 15)):
        return "YELLOW"
    if phase == "YELLOW" and elapsed_s >= 4:
        return "RED"
    if phase == "RED" and elapsed_s >= 30 and queue_len > 0:
        return "GREEN"
    return phase

if __name__ == "__main__":
    assert next_signal_phase("GREEN", 20, True, False, 0) == "YELLOW"
    assert next_signal_phase("GREEN", 20, False, False, 0) == "GREEN"
    assert next_signal_phase("RED", 35, False, False, 3) == "GREEN"
    assert next_signal_phase("RED", 5, False, True, 3) == "ALL_RED"
