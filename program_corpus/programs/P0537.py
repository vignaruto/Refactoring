def future_value_with_deposits(principal: float, rate: float, years: int, deposit: float) -> float:
    if rate == 0:
        return principal + deposit * years
    growth = (1 + rate) ** years
    total = principal * growth + deposit * (growth - 1) / rate * (1 + rate)
    return round(total, 2)

if __name__ == "__main__":
    assert future_value_with_deposits(1000, 0.0, 5, 100) == 1500
    assert future_value_with_deposits(1000, 0.1, 2, 100) == 1441.0
