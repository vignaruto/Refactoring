def count_vowel_consonant(text: str) -> tuple[int, int]:
    vowels = 0
    consonants = 0
    for ch in text.lower():
        if not ch.isalpha():
            continue
        if ch in "aeiou":
            vowels += 1
        else:
            consonants += 1
    return vowels, consonants

if __name__ == "__main__":
    assert count_vowel_consonant("Hello, World!") == (3, 7)
    assert count_vowel_consonant("123") == (0, 0)
