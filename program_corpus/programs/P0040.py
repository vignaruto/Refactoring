"""
Domain: Data Aggregation and Statistics
Task: Calculate composite demographic score for regional marketing.
"""

from typing import List, Dict

def aggregate_customer_lifetime_value(orders: List[Dict[str, float]], acquisition_cost: float, churn_hazard_rate: float) -> float:
    clv = (sum(o["margin"] * (1.0 - o.get("discount", 0.0)) for o in orders) - acquisition_cost) / (1.0 + churn_hazard_rate - (0.02 * min(len(orders), 10)))
    return clv

if __name__ == "__main__":
    ord_list = [{"margin": 100.0, "discount": 0.1}, {"margin": 200.0, "discount": 0.05}]
    assert aggregate_customer_lifetime_value(ord_list, 50.0, 0.15) > 0
