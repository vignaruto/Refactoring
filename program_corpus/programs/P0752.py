def mask_digits(token: str, keep: int = 4, mask: str = "*") -> str:
    digits = [ch for ch in token if ch.isdigit()]
    hide = max(len(digits) - keep, 0)
    out = []
    seen = 0
    for ch in token:
        if ch.isdigit():
            out.append(mask if seen < hide else ch)
            seen += 1
        else:
            out.append(ch)
    return "".join(out)


if __name__ == "__main__":
    assert mask_digits("1234-5678-9012") == "****-****-9012"
    assert mask_digits("12") == "12"
