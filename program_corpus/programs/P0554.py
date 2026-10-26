def looks_like_iso_date(text: str) -> bool:
    parts = text.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    ok = year.isdigit() and month.isdigit() and day.isdigit()
    if ok and len(year) == 4 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
        return True
    return False

if __name__ == "__main__":
    assert looks_like_iso_date("2024-02-29")
    assert not looks_like_iso_date("2024-13-01")
    assert not looks_like_iso_date("24-01-01")
    assert not looks_like_iso_date("2024-1a-01")
    assert not looks_like_iso_date("2024/01/01")
