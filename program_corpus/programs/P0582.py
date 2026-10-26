def common_free_slot(calendars, day_start, day_end, length):
    t = day_start
    while t + length <= day_end:
        clash = False
        for busy in calendars:
            for start, end in busy:
                if start < t + length and t < end and end > start:
                    clash = True
        if not clash:
            return t
        t += 15
    return -1

if __name__ == "__main__":
    cals = [[(540, 600)], [(570, 630), (700, 720)]]
    assert common_free_slot(cals, 480, 1020, 60) == 480
    assert common_free_slot(cals, 540, 1020, 60) == 630
    assert common_free_slot(cals, 540, 600, 60) == -1
