def annual_carrying_cost(order_qty: float, safety_stock: float, unit_cost: float, capital_rate: float, storage_rate: float, obsolescence_rate: float) -> float:
    average_units = order_qty / 2.0 + safety_stock
    carrying_rate = capital_rate + storage_rate + obsolescence_rate
    annual_cost = average_units * unit_cost * carrying_rate
    return round(annual_cost, 2)

if __name__ == "__main__":
    assert annual_carrying_cost(200.0, 50.0, 10.0, 0.1, 0.05, 0.05) == 300.0
