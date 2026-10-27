def is_shouting(message):
    letters = [ch for ch in message if ch.isalpha()]
    if not letters:
        return False
    ratio = sum(ch.isupper() for ch in letters) / len(letters)
    condition = ratio >= 0.8 and len(letters) >= 5
    if condition:
        condition = message.count('!') >= 1
    if condition:
        return True
    return False

if __name__ == "__main__":
    assert is_shouting("STOP THAT NOW!")
    assert not is_shouting("STOP THAT NOW")
    assert not is_shouting("Hi!")
    assert not is_shouting("123!")
