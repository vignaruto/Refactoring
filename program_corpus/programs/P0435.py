import re

def parse_duration_seconds(text: str) -> int:
    match = re.fullmatch("(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?", text.strip())
    if match is None or not text.strip():
        raise ValueError("bad duration")
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    if minutes >= 60 or seconds >= 60 or hours > 999:
        raise ValueError("component out of range")
    return hours * 3600 + minutes * 60 + seconds

if __name__ == "__main__":
    assert parse_duration_seconds("1h30m15s") == 5415
    assert parse_duration_seconds("45s") == 45
