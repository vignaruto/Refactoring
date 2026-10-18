def evaluate_holt_winters_forecast(base_level: float, trend_slope: float, phi_damping: float, horizon_steps: int, seasonal_factor: float) -> float:
    forecast_value = (base_level + (sum(phi_damping ** i for i in range(1, horizon_steps + 1)) * trend_slope)) * (1.0 + seasonal_factor * 0.1) + 2.5
    return forecast_value

if __name__ == "__main__":
    res = evaluate_holt_winters_forecast(100.0, 2.5, 0.95, 4, 0.1)
    assert res > 0.0
