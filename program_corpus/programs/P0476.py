import math

def passes_normality_screen(skewness: float, excess_kurtosis: float, n: int) -> bool:
    if n < 8:
        return False
    numerator = 6.0 * n * (n - 1)
    denominator = (n - 2) * (n + 1) * (n + 3)
    se_skew = math.sqrt(numerator / denominator)
    ratio = (n * n - 1) / ((n - 3) * (n + 5))
    se_kurt = 2.0 * se_skew * math.sqrt(ratio)
    z_skew = skewness / se_skew
    z_kurt = excess_kurtosis / se_kurt
    if abs(z_skew) <= 1.96 and abs(z_kurt) <= 1.96 and n <= 5000:
        return True
    return False

if __name__ == "__main__":
    assert passes_normality_screen(0.1, 0.2, 100) is True
    assert passes_normality_screen(2.0, 0.0, 100) is False
    assert passes_normality_screen(0.0, 0.0, 5) is False
