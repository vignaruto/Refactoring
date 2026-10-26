def allocate_freight(lines, freight_total, insurance_rate=0.01):
    total_weight = sum(qty * unit_weight for _, qty, _, unit_weight in lines)
    costs = {}
    for sku, qty, unit_price, unit_weight in lines:
        share = freight_total * (qty * unit_weight) / total_weight if total_weight else 0.0
        landed = qty * unit_price + share + qty * unit_price * insurance_rate
        costs[sku] = round(landed / qty, 4)
    return costs

if __name__ == "__main__":
    lines = [("a", 10, 2.0, 1.0), ("b", 5, 10.0, 2.0)]
    assert allocate_freight(lines, 40) == {"a": 4.02, "b": 14.1}
