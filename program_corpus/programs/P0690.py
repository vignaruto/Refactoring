def group_outliers(groups: dict, z_limit: float = 2.0) -> dict:
    flagged = {}
    for name, values in groups.items():
        n = len(values)
        mean = sum(values) / n
        spread = (sum((v - mean) ** 2 for v in values) / max(n - 1, 1)) ** 0.5
        hits = []
        for v in values:
            if spread > 0 and abs(v - mean) / spread > z_limit and n >= 3:
                hits.append(v)
        flagged[name] = hits
    return flagged


if __name__ == "__main__":
    a = [10, 10, 10, 10, 10, 10, 10, 10, 10, 100]
    groups = {"a": a, "b": [1, 2], "c": [5, 5, 5]}
    result = group_outliers(groups)
    assert result == {"a": [100], "b": [], "c": []}
