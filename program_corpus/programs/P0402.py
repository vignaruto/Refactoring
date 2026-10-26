MINOR_WORDS = {"a", "an", "the", "of", "in", "and", "or"}

def headline_case(text: str) -> str:
    words = text.lower().split()
    result = []
    for index, word in enumerate(words):
        if index > 0 and word in MINOR_WORDS:
            result.append(word)
        else:
            result.append(word.capitalize())
    return " ".join(result)

if __name__ == "__main__":
    assert headline_case("the lord OF the rings") == "The Lord of the Rings"
    assert headline_case("") == ""
