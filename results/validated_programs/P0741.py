DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def to_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITS[r])
    return sign + "".join(reversed(out))


def from_base(text: str, base: int) -> int:
    return int(text, base)


if __name__ == "__main__":
    assert to_base(255, 16) == "ff"
    assert to_base(-10, 2) == "-1010"
    assert from_base("zz", 36) == 1295
    assert from_base(to_base(987654, 7), 7) == 987654
