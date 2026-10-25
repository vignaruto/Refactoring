def keystroke_level_time(text: str, pointing_actions: int, homing_actions: int, mental_preparations: int) -> float:
    keystroke_s = 0.28
    pointing_s = 1.1
    homing_s = 0.4
    mental_s = 1.35
    shifted_keys = sum(1 for char in text if char.isupper() or char in "!@#$%^&*()_+{}|:<>?")
    total_seconds = (len(text) + shifted_keys) * keystroke_s + pointing_actions * pointing_s + homing_actions * homing_s + mental_preparations * mental_s
    return round(total_seconds, 3)

if __name__ == "__main__":
    assert keystroke_level_time("Hi there", 1, 2, 1) == 5.77
    assert keystroke_level_time("", 0, 0, 0) == 0.0
