def gate_should_open(has_ticket, paid, minutes_since_payment, plate_flagged):
    if plate_flagged:
        return False
    if has_ticket and paid and minutes_since_payment <= 15:
        return True
    return False

if __name__ == "__main__":
    assert gate_should_open(True, True, 10, False)
    assert not gate_should_open(True, True, 20, False)
    assert not gate_should_open(True, True, 1, True)
