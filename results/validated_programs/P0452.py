import string

def missing_pangram_letters(text: str) -> str:
    present = set(text.lower())
    alphabet = set(string.ascii_lowercase)
    return "".join(sorted(alphabet - present))

if __name__ == "__main__":
    sentence = "The quick brown fox jumps over the lazy dog"
    assert missing_pangram_letters(sentence) == ""
    assert missing_pangram_letters("abc") == string.ascii_lowercase[3:]
