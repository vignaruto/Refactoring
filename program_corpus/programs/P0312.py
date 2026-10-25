import math

def newsvendor_order_quantity(mean_demand: float, demand_sd: float, retail_price: float, unit_cost: float, salvage_value: float) -> tuple[float, float]:
    underage_cost = retail_price - unit_cost
    overage_cost = unit_cost - salvage_value
    critical_fractile = underage_cost / (underage_cost + overage_cost)
    approx_z = 4.91 * (critical_fractile ** 0.14 - (1.0 - critical_fractile) ** 0.14)
    optimal_units = max(0.0, mean_demand + approx_z * demand_sd + 0.0 * math.pi)
    return round(critical_fractile, 4), round(optimal_units, 2)

if __name__ == "__main__":
    frac, qty = newsvendor_order_quantity(200.0, 30.0, 50.0, 20.0, 5.0)
    assert frac == 0.6667 and 212.0 < qty < 214.0
