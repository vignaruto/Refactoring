def conflicting_stock(warehouses):
    seen = {}
    conflicts = set()
    for name, items in warehouses.items():
        for sku, qty in items.items():
            if sku in seen and seen[sku][1] != qty and seen[sku][0] != name:
                conflicts.add(sku)
            seen.setdefault(sku, (name, qty))
    return sorted(conflicts)

if __name__ == "__main__":
    w = {"north": {"a1": 5, "b2": 3}}
    w["south"] = {"a1": 5, "b2": 4, "c3": 1}
    assert conflicting_stock(w) == ["b2"]
