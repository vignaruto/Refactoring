def is_hex_color(code: str) -> bool:
    if not code.startswith("#") or len(code) not in (4, 7, 9):
        return False
    for ch in code[1:]:
        if not ("0" <= ch <= "9" or "a" <= ch.lower() <= "f"):
            return False
    return True

if __name__ == "__main__":
    assert is_hex_color("#1a2B3c") is True
    assert is_hex_color("#fff") is True
    assert is_hex_color("#12345g") is False
    assert is_hex_color("123456") is False
