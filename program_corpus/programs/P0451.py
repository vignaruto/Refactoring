def factorial_trailing_zeros(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    zeros = 0
    power_of_five = 5
    while power_of_five <= n:
        zeros += n // power_of_five
        power_of_five *= 5
    return zeros

if __name__ == "__main__":
    assert factorial_trailing_zeros(100) == 24
    assert factorial_trailing_zeros(4) == 0
