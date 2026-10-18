from typing import Dict

def compute_reorder_level(item: Dict[str, float], safety_stock_ratio: float) -> float:
    daily_sales = item.get("avg_daily_sales", 0.0)
    lead_days = item.get("lead_time_days", 0.0)
    demand_during_lead = daily_sales * lead_days
    safety_buffer = demand_during_lead * safety_stock_ratio
    return demand_during_lead + safety_buffer

if __name__ == "__main__":
    prod = {"avg_daily_sales": 15.0, "lead_time_days": 10.0}
    assert compute_reorder_level(prod, 0.2) == 180.0
