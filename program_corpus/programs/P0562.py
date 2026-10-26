def is_question(sentence: str) -> bool:
    text = sentence.strip()
    if not text:
        return False
    first = text.split()[0].lower().strip(",")
    starters = {"who", "what", "why", "how", "is", "can"}
    if text.endswith("?") or first in starters and len(text.split()) > 2 and not text.endswith("."):
        return True
    return False

if __name__ == "__main__":
    assert is_question("Is it raining")
    assert is_question("ok?")
    assert not is_question("Why.")
    assert not is_question("Can you go.")
    assert not is_question("")
