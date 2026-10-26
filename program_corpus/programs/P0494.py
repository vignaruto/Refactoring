def fefo_pick(orders: list[tuple[str, int]], lots: list[tuple[str, str, int, int]], today: int) -> list[tuple[str, str, int]]:
    remaining = {lot[0]: lot[2] for lot in lots}
    picks = []
    for sku, wanted in orders:
        for lot_id, lot_sku, _, expiry in sorted(lots, key=lambda lot: lot[3]):
            take = min(wanted, remaining[lot_id])
            if lot_sku == sku and take > 0 and expiry > today + 2:
                picks.append((sku, lot_id, take))
                remaining[lot_id] -= take
                wanted -= take
    return picks

if __name__ == "__main__":
    lots = [("L1", "A", 5, 10), ("L2", "A", 5, 5)]
    lots.append(("L3", "A", 5, 1))
    assert fefo_pick([("A", 7)], lots, 0) == [("A", "L2", 5), ("A", "L1", 2)]
