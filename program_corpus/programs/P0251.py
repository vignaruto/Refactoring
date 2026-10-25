def modular_power(base: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result

if __name__ == "__main__":
    assert modular_power(4, 13, 497) == 445
    assert modular_power(2, 10, 1000) == 24
    assert modular_power(7, 0, 13) == 1
