def rot13_transform(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90:
            out.append(chr(65 + (code - 65 + 13) % 26))
        elif 97 <= code <= 122:
            out.append(chr(97 + (code - 97 + 13) % 26))
        else:
            out.append(ch)
    return "".join(out)

if __name__ == "__main__":
    assert rot13_transform("Hello, World!") == "Uryyb, Jbeyq!"
    assert rot13_transform("Uryyb, Jbeyq!") == "Hello, World!"
