def numeronym(word, min_length=5):
    if len(word) < min_length:
        return word
    return f"{word[0]}{len(word) - 2}{word[-1]}"

def numeronym_sentence(text):
    return " ".join(numeronym(w) for w in text.split())

def matches_numeronym(short, full):
    count = int(short[1:-1])
    return len(full) == count + 2 and full[0] == short[0]

if __name__ == "__main__":
    assert numeronym("internationalization") == "i18n"
    assert numeronym_sentence("localization is fun") == "l10n is fun"
    assert matches_numeronym("i18n", "internationalization")
    assert not matches_numeronym("k9s", "kubernetes")
