def can_ship_lot(lot: dict, today: int, min_shelf_days: int = 30) -> bool:
    remaining = lot["expiry_day"] - today
    on_hold = lot.get("quality_hold", False)
    if lot["qty"] > 0 and remaining >= min_shelf_days and not on_hold:
        return True
    return False


if __name__ == "__main__":
    lot = {"qty": 5, "expiry_day": 100}
    assert can_ship_lot(lot, 50)
    assert not can_ship_lot(lot, 80)
    assert not can_ship_lot({**lot, "quality_hold": True}, 50)
