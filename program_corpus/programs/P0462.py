def stockout_projection(on_hand: int, daily_demand: float, lead_time_days: int, pending_receipt: int) -> tuple[float, int]:
    days_of_supply = (on_hand + pending_receipt) / daily_demand if daily_demand > 0 else float("inf")
    shortfall_units = max(0, round(daily_demand * lead_time_days - on_hand - pending_receipt))
    return round(days_of_supply, 1), shortfall_units

if __name__ == "__main__":
    assert stockout_projection(100, 20.0, 7, 20) == (6.0, 20)
