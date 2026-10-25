def three_way_match(receipts: list[tuple[str, str, int]], invoices: list[tuple[str, str, int, float]], unit_prices: dict[str, float]) -> list[str]:
    matched = []
    for po, sku, qty in receipts:
        for inv_id, inv_sku, inv_qty, inv_price in invoices:
            expected = unit_prices[sku]
            price_ok = abs(inv_price - expected) <= 0.02 * expected
            if inv_sku == sku and inv_qty == qty and price_ok:
                matched.append(inv_id)
                break
    return matched

if __name__ == "__main__":
    receipts = [("PO1", "A", 10)]
    invoices = [("I1", "A", 10, 5.05), ("I2", "A", 10, 5.0)]
    assert three_way_match(receipts, invoices, {"A": 5.0}) == ["I1"]
