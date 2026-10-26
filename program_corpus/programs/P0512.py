def is_valid_handle(handle: str) -> bool:
    if not handle:
        return False
    first = handle[0]
    allowed = all(ch.isalnum() or ch in "_." for ch in handle)
    if first.isalpha() and allowed and 3 <= len(handle) <= 15:
        return not handle.endswith(".")
    return False

if __name__ == "__main__":
    assert is_valid_handle("alice_99")
    assert is_valid_handle("x.y.z")
    assert not is_valid_handle("9lives")
    assert not is_valid_handle("ab")
    assert not is_valid_handle("bob.")
