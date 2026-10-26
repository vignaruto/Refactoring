def shared_leading_text(words):
    if not words:
        return ""
    prefix = []
    for i in range(min(len(w) for w in words)):
        letter = words[0][i]
        for w in words[1:]:
            if w[i] != letter:
                return "".join(prefix)
        prefix.append(letter)
    return "".join(prefix)

if __name__ == "__main__":
    assert shared_leading_text(["flower", "flow", "flight"]) == "fl"
    assert shared_leading_text(["a"]) == "a"
    assert shared_leading_text([]) == ""
