def min_max_normalize_vector(
    values: list[float]
) -> list[float]:
    if not values:
        return []
    min_val = min(values)
    max_val = max(values)
    spread = max_val - min_val
    if spread == 0.0:
        return [0.0] * len(values)
    normalized = []
    for x in values:
        norm = (x - min_val) / spread
        normalized.append(round(norm, 4))
    return normalized

if __name__ == "__main__":
    nums = [10.0, 20.0, 30.0, 40.0, 50.0]
    res = min_max_normalize_vector(nums)
    assert res[0] == 0.0 and res[-1] == 1.0
