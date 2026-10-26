PHASES = (("green", 30), ("yellow", 5), ("red", 25))

def light_at_time(seconds: int) -> str:
    cycle = sum(duration for _, duration in PHASES)
    offset = seconds % cycle
    for colour, duration in PHASES:
        if offset < duration:
            return colour
        offset -= duration
    return "red"

if __name__ == "__main__":
    assert light_at_time(0) == "green"
    assert light_at_time(32) == "yellow"
    assert light_at_time(59) == "red"
    assert light_at_time(60) == "green"
