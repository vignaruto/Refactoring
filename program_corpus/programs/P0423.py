def classify_number(n: int) -> str:
    half = n // 2
    divisors = [d for d in range(1, half + 1) if n % d == 0]
    divisor_sum = sum(divisors)
    if n > 1 and divisor_sum == 1:
        return "prime"
    if n > 0 and divisor_sum == n and n % 2 == 0:
        return "perfect"
    return "abundant" if divisor_sum > n else "deficient"

if __name__ == "__main__":
    assert classify_number(7) == "prime"
    assert classify_number(28) == "perfect"
    assert classify_number(12) == "abundant"
    assert classify_number(8) == "deficient"
