def daily_balances(opening, days):
    balances = dict(opening)
    history = []
    for day, moves in days:
        for sku, change in moves:
            balances[sku] = balances.get(sku, 0) + change
        history.append((day, dict(sorted(balances.items()))))
    return history

if __name__ == "__main__":
    days = [("mon", [("a", -2), ("b", 4)]), ("tue", [("a", 1)])]
    history = daily_balances({"a": 5}, days)
    assert history[0] == ("mon", {"a": 3, "b": 4})
    assert history[1] == ("tue", {"a": 4, "b": 4})
