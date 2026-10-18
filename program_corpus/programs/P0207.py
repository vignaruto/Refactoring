def compute_inventory_turnover_days(
    cost_of_goods_sold: float, beg_inventory: float, end_inventory: float
) -> dict[str, float]:
    avg_inventory = (beg_inventory + end_inventory) / 2.0
    if avg_inventory <= 0.0:
        raise ValueError("Average inventory must be positive")
    turns = cost_of_goods_sold / avg_inventory
    days = 365.0 / turns if turns > 0.0 else 0.0
    return {
        "turnover_ratio": round(turns, 2),
        "days_in_inventory": round(days, 1)
    }

if __name__ == "__main__":
    res = compute_inventory_turnover_days(400000.0, 80000.0, 120000.0)
    assert res["turnover_ratio"] == 4.0
