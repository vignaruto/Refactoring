def niven_numbers_upto(limit: int) -> list[int]:
    found = []
    for n in range(1, limit + 1):
        digit_sum = sum(int(d) for d in str(n))
        if n % digit_sum == 0:
            found.append(n)
    return found

if __name__ == "__main__":
    assert niven_numbers_upto(12) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
    assert niven_numbers_upto(0) == []
