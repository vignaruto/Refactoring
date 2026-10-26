def readings_until_alarm(readings, limit, max_count):
    total = 0.0
    i = 0
    while i < len(readings) and i < max_count and total + readings[i] <= limit:
        total += readings[i]
        i += 1
    return i, round(total, 2)

if __name__ == "__main__":
    assert readings_until_alarm([2.5, 3.0, 4.0, 1.0], 6.0, 10) == (2, 5.5)
    assert readings_until_alarm([1, 1, 1], 10, 2) == (2, 2.0)
    assert readings_until_alarm([], 5, 5) == (0, 0.0)
