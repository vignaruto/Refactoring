def merge_user_settings(defaults: dict, overrides: dict, locked: set) -> dict:
    merged = dict(defaults)
    for key, value in overrides.items():
        known = key in defaults
        same_type = known and type(value) is type(defaults[key])
        if known and same_type and key not in locked:
            merged[key] = value
    return merged

if __name__ == "__main__":
    base = {"theme": "light", "font": 12, "beta": False}
    new = {"theme": "dark", "font": "big", "beta": True}
    expected = {"theme": "dark", "font": 12, "beta": False}
    assert merge_user_settings(base, new, {"beta"}) == expected
