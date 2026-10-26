def reorder_urgency(on_hand, daily_demand, lead_time_days, safety_days=3, on_order=0):
    projected = on_hand + on_order - daily_demand * lead_time_days - daily_demand * safety_days
    if projected < 0 and on_order == 0 or on_hand < daily_demand:
        return "urgent", projected
    if projected < daily_demand * 7:
        return "soon", projected
    return "ok", projected

if __name__ == "__main__":
    assert reorder_urgency(10, 5, 4) == ("urgent", -25)
    assert reorder_urgency(100, 5, 4) == ("ok", 65)
    assert reorder_urgency(50, 5, 4) == ("soon", 15)
    assert reorder_urgency(40, 5, 4, on_order=50) == ("ok", 55)
