def deduct_stock_fifo(
    batches: list[dict[str, float]], req_qty: float
) -> float:
    remaining_req = req_qty
    total_cost = 0.0
    for b in batches:
        if remaining_req <= 0.0:
            break
        take = min(b["qty"], remaining_req)
        b["qty"] -= take
        total_cost += take * b["cost"]
        remaining_req -= take
    return total_cost

if __name__ == "__main__":
    st = [{"qty": 10.0, "cost": 2.0}, {"qty": 10.0, "cost": 3.0}]
    cost = deduct_stock_fifo(st, 15.0)
    assert cost == 35.0
