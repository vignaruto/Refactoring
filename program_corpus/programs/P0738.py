def weekly_pay(hours_by_day, rate, weekend_days=("sat", "sun")):
    pay = 0.0
    total_hours = 0
    for day, hours in hours_by_day.items():
        total_hours += hours
        weekend = day in weekend_days
        if weekend and hours > 0 or hours > 10 or total_hours > 40:
            pay += hours * rate * 1.5 + (hours - 8) * rate * 0.25 * (hours > 8)
        else:
            pay += hours * rate
    return round(pay, 2)

if __name__ == "__main__":
    assert weekly_pay({"mon": 8, "sat": 4}, 10) == 140.0
    assert weekly_pay({"mon": 12}, 10) == 190.0
