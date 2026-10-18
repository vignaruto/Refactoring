def compute_iqr_fences(data: list[float]) -> dict[str, float]:
    if len(data) < 4:
        raise ValueError("At least 4 observations required")
    sorted_d = sorted(data)
    n = len(sorted_d)
    q1 = sorted_d[n // 4]
    q3 = sorted_d[(3 * n) // 4]
    iqr = q3 - q1
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_fence": q1 - 1.5 * iqr,
        "upper_fence": q3 + 1.5 * iqr
    }

if __name__ == "__main__":
    res = compute_iqr_fences([10.0, 12.0, 14.0, 15.0, 18.0, 20.0, 22.0, 50.0])
    assert res["iqr"] == 8.0
