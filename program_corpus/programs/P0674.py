def inventory_valuation(items, freight_rate=0.05, duty_rate=0.1):
    total = 0.0
    for item in items:
        base = item["qty"] * item["unit_cost"]
        total += base + base * freight_rate + base * duty_rate * item.get("imported", 0)
    return round(total, 2)

if __name__ == "__main__":
    local = {"qty": 10, "unit_cost": 2.0}
    imported = {"qty": 1, "unit_cost": 100.0, "imported": 1}
    assert inventory_valuation([local, imported]) == 136.0
    assert inventory_valuation([]) == 0.0
