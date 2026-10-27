def compress_character_runs(text: str) -> str:
    if not text:
        return ""
    chunks = []
    curr = text[0]
    count = 1
    for char in text[1:]:
        if char == curr:
            count += 1
        else:
            chunks.append(f"{curr}{count}")
            curr = char
            count = 1
    chunks.append(f"{curr}{count}")
    return "".join(chunks)

if __name__ == "__main__":
    assert compress_character_runs("aaabbc") == "a3b2c1"
