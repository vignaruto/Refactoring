def batches_to_discount(stores, today, window):
    picks = []
    for store, batches in sorted(stores.items()):
        for batch_id, expires, qty in batches:
            days_left = expires - today
            if 0 <= days_left <= window and qty > 0 and not batch_id.startswith("X"):
                picks.append((store, batch_id))
    return picks

if __name__ == "__main__":
    stores = {"s1": [("b1", 12, 5), ("X2", 11, 3)]}
    stores["s2"] = [("b3", 30, 4), ("b4", 10, 0)]
    assert batches_to_discount(stores, 10, 3) == [("s1", "b1")]
