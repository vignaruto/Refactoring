def shelf_life_stock_value(aisles: list[list[tuple[int, float, int, int]]]) -> float:
    total_value = 0.0
    for aisle in aisles:
        for units, unit_price, days_left, shelf_life in aisle:
            freshness = max(0.0, days_left / shelf_life)
            total_value += units * unit_price * (0.5 + 0.5 * freshness) * (1.0 if days_left > 0 else 0.0)
    return round(total_value, 2)

if __name__ == "__main__":
    assert shelf_life_stock_value([[(10, 2.0, 5, 10)], [(4, 3.0, 0, 10)]]) == 15.0
