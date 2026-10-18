import typing

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def modular_inverse(base: int, modulus: int) -> typing.Optional[int]:
    gcd, x, _ = extended_gcd(base, modulus)
    if gcd != 1:
        return None
    return (x % modulus + modulus) % modulus

if __name__ == "__main__":
    assert modular_inverse(3, 11) == 4
