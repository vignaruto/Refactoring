def r_squared(actual, fitted, predictors=1):
    n = len(actual)
    mean = sum(actual) / n
    errors = [a - f for a, f in zip(actual, fitted)]
    residual_sum = sum(e * e for e in errors)
    total_sum = sum((a - mean) ** 2 for a in actual)
    if not total_sum or n <= predictors + 1:
        return 0.0, 0.0
    plain = 1 - residual_sum / total_sum
    adjusted = 1 - residual_sum / total_sum * (n - 1) / (n - predictors - 1)
    return round(plain, 4), round(adjusted, 4)

if __name__ == "__main__":
    fitted = [1.1, 1.9, 3.2, 3.8]
    assert r_squared([1, 2, 3, 4], fitted) == (0.98, 0.97)
    assert r_squared([1, 2, 3], [1, 2, 3]) == (1.0, 1.0)
    assert r_squared([2, 2, 2], [2, 2, 2]) == (0.0, 0.0)
