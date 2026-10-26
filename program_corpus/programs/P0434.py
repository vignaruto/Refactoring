import math

def ab_test_verdict(conversions_a: int, visitors_a: int, conversions_b: int, visitors_b: int) -> str:
    rate_a, rate_b = conversions_a / visitors_a, conversions_b / visitors_b
    pooled = (conversions_a + conversions_b) / (visitors_a + visitors_b)
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / visitors_a + 1 / visitors_b))
    z_score = (rate_b - rate_a) / standard_error if standard_error > 0 else 0.0
    if z_score > 1.96 and visitors_a >= 100 and visitors_b >= 100:
        return "B wins"
    if z_score < -1.96 and visitors_a >= 100 and visitors_b >= 100:
        return "A wins"
    return "inconclusive"

if __name__ == "__main__":
    assert ab_test_verdict(100, 1000, 150, 1000) == "B wins"
    assert ab_test_verdict(10, 50, 20, 50) == "inconclusive"
