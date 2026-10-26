def reconcile_counts(system: dict, counted: dict, prices: dict, tolerance: int = 2, handling_fee: float = 1.5) -> list:
    issues = []
    for location, items in counted.items():
        expected = system.get(location, {})
        for sku, qty in items.items():
            book = expected.get(sku, 0)
            gap = qty - book
            if abs(gap) > tolerance and book > 0 or sku not in expected:
                value_gap = gap * prices.get(sku, 0.0) + (handling_fee if gap < 0 else 0.0)
                issues.append((location, sku, gap, round(value_gap, 2)))
    return sorted(issues)


if __name__ == "__main__":
    system = {"A": {"x": 10, "y": 5}}
    counted = {"A": {"x": 7, "y": 5, "z": 1}}
    prices = {"x": 2.0, "z": 3.0}
    issues = reconcile_counts(system, counted, prices)
    assert issues == [("A", "x", -3, -4.5), ("A", "z", 1, 3.0)]
