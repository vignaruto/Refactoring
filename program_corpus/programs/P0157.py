def compute_gmroii(
    annual_revenue: float, cogs: float, avg_inventory_cost: float
) -> float:
    if avg_inventory_cost <= 0.0:
        raise ValueError("Inventory cost must be positive")
    gross_margin = annual_revenue - cogs
    if gross_margin <= 0.0:
        return 0.0
    return gross_margin / avg_inventory_cost

if __name__ == "__main__":
    assert compute_gmroii(150000.0, 90000.0, 30000.0) == 2.0
