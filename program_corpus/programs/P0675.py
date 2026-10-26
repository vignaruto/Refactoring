def hhmm(minute):
    return f"{minute // 60:02d}:{minute % 60:02d}"


def build_agenda(start_minute, items, gap=5):
    agenda = []
    clock = start_minute
    for title, minutes in items:
        agenda.append((hhmm(clock), hhmm(clock + minutes), title, minutes >= 30))
        clock += minutes + gap
    return agenda


if __name__ == "__main__":
    items = [("intro", 10), ("review", 45)]
    agenda = build_agenda(540, items)
    assert agenda[0] == ("09:00", "09:10", "intro", False)
    assert agenda[1] == ("09:15", "10:00", "review", True)
