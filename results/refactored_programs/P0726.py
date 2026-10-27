def category_summary(rows, min_count=2, max_cv=0.5, population=100):
    groups = {}
    for category, value in rows:
        groups.setdefault(category, []).append(value)
    summary = {}
    for category, values in sorted(groups.items()):
        n = len(values)
        mean = sum(values) / n
        sq = 0.0
        for v in values:
            sq += (v - mean) ** 2
        std = (sq / n) ** 0.5
        cv = std / mean if mean else float("inf")
        margin = 1.96 * std / n ** 0.5
        part = ((population - n) / max(population - 1, 1)) ** 0.5
        margin = margin * part
        condition = n >= min_count and cv <= max_cv and mean > 0
        if condition:
            summary[category] = (n, round(mean, 2), round(margin, 2))
    return summary

if __name__ == "__main__":
    rows = [("a", 10), ("a", 12), ("b", 5)]
    rows.extend([("c", 1), ("c", 100)])
    assert category_summary(rows) == {"a": (2, 11.0, 1.38)}
