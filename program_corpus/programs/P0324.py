def can_store_lot_in_bin(free_slots: int, pallets: int, cold_lot: bool, cold_bin: bool, temp_c: float, locked: bool) -> bool:
    if locked or pallets <= 0 or free_slots < pallets:
        return False
    if cold_lot and (not cold_bin or temp_c > 4.0):
        return False
    return True

if __name__ == "__main__":
    assert can_store_lot_in_bin(6, 3, True, True, 2.5, False) is True
    assert can_store_lot_in_bin(6, 3, True, True, 8.0, False) is False
    assert can_store_lot_in_bin(2, 5, False, False, 20.0, False) is False
