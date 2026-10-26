def is_hex_colour(token):
    body = token[1:]
    hex_digits = set("0123456789abcdefABCDEF")
    if token.startswith("#") and len(body) in (3, 6) and set(body) <= hex_digits:
        return True
    return False

if __name__ == "__main__":
    assert is_hex_colour("#fa0")
    assert is_hex_colour("#FFAA00")
    assert not is_hex_colour("#ffaa0")
    assert not is_hex_colour("ffaa00")
    assert not is_hex_colour("#ggg")
