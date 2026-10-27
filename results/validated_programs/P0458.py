def parse_bin_location(code: str) -> tuple[str, int, int]:
    parts = code.upper().split("-")
    if len(parts) != 3:
        raise ValueError("expected AISLE-RACK-LEVEL")
    aisle, rack, level = parts
    return aisle, int(rack), int(level)

if __name__ == "__main__":
    assert parse_bin_location("a-12-3") == ("A", 12, 3)
