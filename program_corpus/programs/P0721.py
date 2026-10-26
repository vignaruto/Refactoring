def stock_age_value(warehouses: dict, today: int, holding_rate: float = 0.002) -> dict:
    report = {}
    for site, lots in warehouses.items():
        cost = 0.0
        for qty, unit_cost, received_day in lots:
            age = today - received_day
            carrying = qty * unit_cost * holding_rate * age + qty * unit_cost * (age > 180) * 0.1
            cost += carrying
        report[site] = round(cost, 2)
    return report


if __name__ == "__main__":
    lots = {"w1": [(10, 5.0, 190)], "w2": [(1, 100.0, 0)]}
    assert stock_age_value(lots, 200) == {"w1": 1.0, "w2": 50.0}
