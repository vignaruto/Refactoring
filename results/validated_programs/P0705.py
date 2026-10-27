def best_quarter(sales: dict) -> dict:
    totals = {}
    for region, quarters in sales.items():
        for quarter, amounts in quarters.items():
            totals[(region, quarter)] = sum(amounts)
    best = {}
    for (region, quarter), total in sorted(totals.items()):
        if total > best.get(region, (None, -1))[1]:
            best[region] = (quarter, total)
    return best


if __name__ == "__main__":
    sales = {"n": {"q1": [1, 2], "q2": [5]}, "s": {"q1": [4]}}
    assert best_quarter(sales) == {"n": ("q2", 5), "s": ("q1", 4)}
