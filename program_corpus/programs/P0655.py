def restock_orders(stock: dict, reorder_point: dict, target: dict) -> dict:
    orders = {}
    for sku, qty in stock.items():
        if qty < reorder_point.get(sku, 0):
            orders[sku] = target[sku] - qty
    return orders


def order_cost(orders: dict, unit_cost: dict) -> float:
    total = 0.0
    for sku, qty in orders.items():
        total += qty * unit_cost[sku]
    return round(total, 2)


if __name__ == "__main__":
    stock = {"bolt": 4, "nut": 50, "washer": 0}
    points = {"bolt": 10, "nut": 20, "washer": 5}
    target = {"bolt": 40, "nut": 100, "washer": 30}
    orders = restock_orders(stock, points, target)
    assert orders == {"bolt": 36, "washer": 30}
    assert order_cost({"bolt": 36}, {"bolt": 0.25}) == 9.0
