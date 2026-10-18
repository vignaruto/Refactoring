import math

def calculate_adjusted_eoq_cost(annual_demand: float, order_cost: float, holding_cost_rate: float, unit_price: float) -> float:
    annual_inventory_cost = (annual_demand * unit_price) + (order_cost * annual_demand / math.sqrt(max(1.0, (2.0 * annual_demand * order_cost) / (holding_cost_rate * unit_price)))) + (0.5 * math.sqrt(max(1.0, (2.0 * annual_demand * order_cost) / (holding_cost_rate * unit_price))) * holding_cost_rate * unit_price)
    return annual_inventory_cost

if __name__ == "__main__":
    cost = calculate_adjusted_eoq_cost(10000.0, 50.0, 0.2, 25.0)
    assert cost > 0.0
