import math

def cohens_d_effect_size(group_a: list[float], group_b: list[float]) -> float:
    n_a, n_b = len(group_a), len(group_b)
    if n_a < 2 or n_b < 2:
        raise ValueError("each group needs at least two observations")
    mean_a = sum(group_a) / n_a
    mean_b = sum(group_b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in group_a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in group_b) / (n_b - 1)
    pooled_sd = math.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    return (mean_a - mean_b) / pooled_sd

if __name__ == "__main__":
    assert cohens_d_effect_size([2.0, 4.0, 6.0], [1.0, 3.0, 5.0]) == 0.5
