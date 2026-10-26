def flag_store_anomalies(sales, z_limit):
    flagged = []
    for store, weeks in sorted(sales.items()):
        mean = sum(weeks) / len(weeks)
        spread = (sum((w - mean) ** 2 for w in weeks) / max(1, len(weeks) - 1)) ** 0.5
        for week, value in enumerate(weeks):
            if spread > 0 and abs(value - mean) / spread > z_limit and value != 0:
                flagged.append((store, week))
    return flagged

if __name__ == "__main__":
    sales = {"s1": [10, 10, 10, 50], "s2": [5, 5]}
    assert flag_store_anomalies(sales, 1.4) == [("s1", 3)]
