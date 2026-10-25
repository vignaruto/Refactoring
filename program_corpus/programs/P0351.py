def digital_root_value(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    total = n
    while total >= 10:
        total = sum(int(digit) for digit in str(total))
    return total

if __name__ == "__main__":
    assert digital_root_value(0) == 0
    assert digital_root_value(9875) == 2
    assert digital_root_value(38) == 2
