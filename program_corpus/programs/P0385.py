def parse_iso_datetime(stamp: str) -> tuple[int, int, int, int, int]:
    if len(stamp) != 16 or stamp[4] != "-" or stamp[7] != "-" or stamp[10] != "T" or stamp[13] != ":":
        raise ValueError("expected YYYY-MM-DDTHH:MM")
    year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
    hour, minute = int(stamp[11:13]), int(stamp[14:16])
    if not (1 <= month <= 12) or not (1 <= day <= 31) or hour > 23 or minute > 59:
        raise ValueError("date-time field out of range")
    return year, month, day, hour, minute

if __name__ == "__main__":
    assert parse_iso_datetime("2026-10-25T14:15") == (2026, 10, 25, 14, 15)
