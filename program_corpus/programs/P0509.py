def should_place_reorder(sku: dict, daily_demand: float, lead_days: int) -> bool:
    on_hand = sku["on_hand"] + sku.get("incoming", 0)
    safety = sku.get("safety_stock", 0)
    projected = on_hand - daily_demand * lead_days
    if sku.get("discontinued"):
        return False
    if projected < safety and daily_demand > 0 and not sku.get("frozen", False):
        return True
    return False

if __name__ == "__main__":
    item = {"on_hand": 20, "incoming": 5, "safety_stock": 10}
    assert should_place_reorder(item, 4.0, 5)
    assert not should_place_reorder(item, 2.0, 5)
    assert not should_place_reorder({"on_hand": 0, "frozen": True}, 1.0, 3)
