def advance_signal_phase(phase: str, waiting: int, elapsed: int, emergency: bool) -> str:
    if emergency:
        return "all_red"
    if phase == "green" and elapsed >= 30 and waiting > 0:
        return "yellow"
    if phase == "yellow" and elapsed >= 4:
        return "red"
    if phase == "red" and (elapsed >= 25 or waiting > 5):
        return "green"
    return phase

if __name__ == "__main__":
    assert advance_signal_phase("green", 3, 31, False) == "yellow"
    assert advance_signal_phase("green", 0, 31, False) == "green"
    assert advance_signal_phase("red", 6, 10, False) == "green"
    assert advance_signal_phase("yellow", 0, 1, True) == "all_red"
