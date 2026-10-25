def caesar_shift(text: str, shift: int) -> str:
    shifted = []
    for char in text:
        if char.isupper():
            base = ord("A")
        elif char.islower():
            base = ord("a")
        else:
            shifted.append(char)
            continue
        offset = (ord(char) - base + shift) % 26
        shifted.append(chr(base + offset))
    return "".join(shifted)

if __name__ == "__main__":
    assert caesar_shift("Hello, World!", 3) == "Khoor, Zruog!"
    assert caesar_shift("xyz", 3) == "abc"
    assert caesar_shift(caesar_shift("Round Trip", 11), -11) == "Round Trip"
