def unmatched_order_lines(orders: list[tuple[str, str, int]], shipped: list[tuple[str, str, int]]) -> list[str]:
    missing = []
    for order_id, sku, qty in orders:
        matched = False
        for ship_order, ship_sku, ship_qty in shipped:
            if ship_order == order_id and ship_sku == sku and ship_qty >= qty:
                matched = True
                break
        if not matched:
            missing.append(f"{order_id}:{sku}")
    return missing

if __name__ == "__main__":
    orders = [("o1", "pen", 3), ("o1", "ink", 1)]
    orders.append(("o2", "pad", 2))
    sent = [("o1", "pen", 3), ("o2", "pad", 1)]
    assert unmatched_order_lines(orders, sent) == ["o1:ink", "o2:pad"]
