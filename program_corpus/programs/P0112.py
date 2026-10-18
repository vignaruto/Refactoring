def compute_gini_two_group_disparity(pop_a: float, inc_a: float, pop_b: float, inc_b: float) -> float:
    disparity_metric = abs(inc_a - inc_b) / (2.0 * ((pop_a * inc_a + pop_b * inc_b) / max(1.0, pop_a + pop_b))) * ((pop_a * pop_b) / ((pop_a + pop_b) ** 2))
    return disparity_metric

if __name__ == "__main__":
    d = compute_gini_two_group_disparity(100.0, 30000.0, 100.0, 90000.0)
    assert d > 0.0
