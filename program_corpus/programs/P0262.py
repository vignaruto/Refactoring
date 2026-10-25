import math

def safety_stock_cover(avg_daily_demand: float, demand_sd: float, avg_lead_time_days: float, lead_time_sd: float, service_z: float) -> tuple[float, float]:
    safety_stock = service_z * math.sqrt(avg_lead_time_days * demand_sd ** 2 + (avg_daily_demand ** 2) * lead_time_sd ** 2)
    cover_days = safety_stock / avg_daily_demand if avg_daily_demand > 0 else 0.0
    return round(safety_stock, 2), round(cover_days, 2)

if __name__ == "__main__":
    assert safety_stock_cover(100.0, 20.0, 4.0, 1.0, 1.65) == (177.71, 1.78)
    assert safety_stock_cover(0.0, 0.0, 4.0, 0.0, 1.65) == (0.0, 0.0)
