def stock_valuation(lots: list[tuple[int, float, float]]) -> float:
    value = 0.0
    for qty, unit_cost, damage_rate in lots:
        value += qty * unit_cost * (1 - damage_rate) + qty * 0.15 * (unit_cost > 100)
    return round(value, 2)

if __name__ == "__main__":
    lots = [(10, 50.0, 0.1), (2, 200.0, 0.0)]
    assert stock_valuation(lots) == 850.3
    assert stock_valuation([]) == 0.0
