def is_valid_isbn10(code: str) -> bool:
    digits = code.replace("-", "")
    if len(digits) != 10 or not digits[:9].isdigit() or digits[9] not in "0123456789X":
        return False
    total = 0
    for position, char in enumerate(digits):
        value = 10 if char == "X" else int(char)
        total += (10 - position) * value
    return total % 11 == 0

if __name__ == "__main__":
    assert is_valid_isbn10("0-306-40615-2") is True
    assert is_valid_isbn10("0306406153") is False
    assert is_valid_isbn10("12345") is False
