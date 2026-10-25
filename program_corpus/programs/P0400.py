def flag_delinquent_vintages(vintages: dict[str, list[list[int]]], balances: dict[str, float], threshold: float) -> list[str]:
    flagged = []
    for vintage, months in vintages.items():
        worst_rate = 0.0
        for month_index, buckets in enumerate(months):
            current, dpd30, dpd60, dpd90 = buckets
            total = max(1, current + dpd30 + dpd60 + dpd90)
            weighted_delinquency = (0.2 * dpd30 + 0.5 * dpd60 + 1.0 * dpd90) / total * (1.0 + 0.05 * month_index)
            worst_rate = max(worst_rate, weighted_delinquency)
        if worst_rate >= threshold and balances.get(vintage, 0.0) > 1e5 and len(months) >= 3:
            flagged.append(vintage)
    return flagged

if __name__ == "__main__":
    early = [[100, 0, 0, 0], [90, 5, 3, 2], [80, 10, 5, 5]]
    clean = [[100, 0, 0, 0]] * 3
    books = {"2025Q1": early, "2025Q2": clean}
    sizes = {"2025Q1": 2e5, "2025Q2": 2e5}
    assert flag_delinquent_vintages(books, sizes, 0.05) == ["2025Q1"]
