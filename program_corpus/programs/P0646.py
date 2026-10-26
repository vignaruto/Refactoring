from math import sqrt

def order_quantity_plan(annual_demand, order_cost, unit_cost, holding_rate, on_hand):
    eoq = sqrt(2 * annual_demand * order_cost / (unit_cost * holding_rate))
    reorder = max(0, round(eoq) - on_hand + int(annual_demand / 365 * 7) - int(on_hand * 0.1))
    return reorder

if __name__ == "__main__":
    assert order_quantity_plan(1000, 50, 10, 0.2, 100) == 133
    assert order_quantity_plan(1000, 50, 10, 0.2, 5000) == 0
