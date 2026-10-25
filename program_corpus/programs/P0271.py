def is_valid_ipv4(address: str) -> bool:
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or (len(part) > 1 and part[0] == "0") or int(part) > 255:
            return False
    return True

if __name__ == "__main__":
    assert is_valid_ipv4("192.168.0.1") is True
    assert is_valid_ipv4("256.1.1.1") is False
    assert is_valid_ipv4("10.01.0.1") is False
    assert is_valid_ipv4("1.2.3") is False
