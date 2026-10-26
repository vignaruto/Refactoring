def savings_value(principal, deposit, annual_rate, years, due=0):
    rate = annual_rate / 12
    n = years * 12
    if rate == 0:
        return round(principal + deposit * n, 2)
    growth = (1 + rate) ** n
    value = principal * growth + deposit * (growth - 1) / rate * (1 + rate * due)
    return round(value, 2)

if __name__ == "__main__":
    assert savings_value(1000, 0, 0.0, 5) == 1000
    assert savings_value(0, 100, 0.0, 1) == 1200
    assert savings_value(1000, 0, 0.12, 1) == 1126.83
