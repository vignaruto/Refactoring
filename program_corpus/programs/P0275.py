def is_valid_gregorian_date(year: int, month: int, day: int) -> bool:
    if year < 1583 or month < 1 or month > 12 or day < 1:
        return False
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        february_days = 29
    else:
        february_days = 28
    if month == 2:
        return day <= february_days
    if month in (4, 6, 9, 11):
        return day <= 30
    return day <= 31

if __name__ == "__main__":
    assert is_valid_gregorian_date(2024, 2, 29) is True
    assert is_valid_gregorian_date(1900, 2, 29) is False
    assert is_valid_gregorian_date(2000, 2, 29) is True
    assert is_valid_gregorian_date(2023, 4, 31) is False
    assert is_valid_gregorian_date(2023, 13, 1) is False
