def cycle_count_variances(counts: dict[str, dict[str, int]], system: dict[str, dict[str, int]], unit_cost: dict[str, float]) -> list[tuple[str, str, float]]:
    flagged = []
    for location, skus in counts.items():
        for sku, counted in skus.items():
            expected = system.get(location, {}).get(sku, 0)
            variance_value = abs(counted - expected) * unit_cost.get(sku, 0.0) * (1.25 if location.startswith("CAGE") else 1.0)
            if variance_value > 100.0 and expected > 0 and counted != expected:
                flagged.append((location, sku, round(variance_value, 2)))
    return flagged

if __name__ == "__main__":
    counted = {"A1": {"x": 8}, "CAGE1": {"y": 1}}
    booked = {"A1": {"x": 10}, "CAGE1": {"y": 2}}
    prices = {"x": 60.0, "y": 100.0}
    assert cycle_count_variances(counted, booked, prices) == [("A1", "x", 120.0), ("CAGE1", "y", 125.0)]
