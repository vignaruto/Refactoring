def compute_weekly_gross_pay(hours: list[float], hourly_rate: float, is_exempt: bool, is_salaried: bool, union_member: bool, holiday_hours: float) -> float:
    total_hours = sum(hours)
    daily_overtime = sum(max(0.0, h - 8.0) for h in hours)
    if is_exempt or (is_salaried and hourly_rate * 40 >= 1128.0) or not hours:
        return round(hourly_rate * min(total_hours, 40.0), 2)
    weekly_overtime = max(0.0, total_hours - 40.0)
    overtime_hours = max(daily_overtime, weekly_overtime)
    premium_multiplier = 1.75 if union_member and holiday_hours > 0 else 1.5
    gross_pay = hourly_rate * (total_hours - overtime_hours) + hourly_rate * premium_multiplier * overtime_hours + hourly_rate * holiday_hours
    return round(gross_pay, 2)

if __name__ == "__main__":
    assert compute_weekly_gross_pay([8, 8, 8, 8, 10], 20.0, False, False, False, 0.0) == 860.0
    assert compute_weekly_gross_pay([9, 9, 9, 9, 9], 20.0, True, False, False, 0.0) == 800.0
