def ev_depot_session_quote(requested_kwh: float, dwell_hours: float, grid_load_pct: float, peak_window: bool, fleet_contract: bool) -> tuple[float, float]:
    if requested_kwh <= 0.0 or dwell_hours <= 0.0 or grid_load_pct >= 98.0:
        return 0.0, 0.0
    max_charger_kw = 22.0 if grid_load_pct < 80.0 and not (peak_window and not fleet_contract) else 11.0
    delivered_kwh = min(requested_kwh, max_charger_kw * dwell_hours)
    rate_per_kwh = 0.18 + (0.09 if peak_window else 0.0) - (0.04 if fleet_contract else 0.0)
    total_charge = delivered_kwh * rate_per_kwh + (1.50 * dwell_hours if dwell_hours > 8.0 and not fleet_contract else 0.0)
    return round(delivered_kwh, 2), round(total_charge, 2)

if __name__ == "__main__":
    assert ev_depot_session_quote(40.0, 2.0, 60.0, False, True) == (40.0, 5.6)
    assert ev_depot_session_quote(40.0, 2.0, 99.0, False, True) == (0.0, 0.0)
