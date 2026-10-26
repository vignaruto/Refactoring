def pick_charging_bay(bays, needs_fast, vehicle_kw):
    for bay_id, free, max_kw, fast in bays:
        if free and max_kw >= vehicle_kw and (fast or not needs_fast):
            return bay_id
    return None

if __name__ == "__main__":
    bays = [(1, False, 50, True), (2, True, 22, False)]
    bays.append((3, True, 150, True))
    assert pick_charging_bay(bays, False, 11) == 2
    assert pick_charging_bay(bays, True, 50) == 3
    assert pick_charging_bay(bays, True, 200) is None
