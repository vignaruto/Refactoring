def spelling_suggestions(text: str, dictionary: set[str], max_suggestions: int = 3) -> dict[str, list[str]]:
    letters = "abcdefghijklmnopqrstuvwxyz"
    suggestions = {}
    for word in text.lower().split():
        if word in dictionary or not word.isalpha():
            continue
        candidates = set()
        for i in range(len(word) + 1):
            for ch in letters:
                candidates.add(word[:i] + ch + word[i:])
                if i < len(word) and ch != word[i] and word[:i] + ch + word[i + 1:] in dictionary:
                    candidates.add(word[:i] + ch + word[i + 1:])
            candidates.add(word[:i] + word[i + 1:])
        suggestions[word] = sorted(candidates & dictionary)[:max_suggestions]
    return suggestions

if __name__ == "__main__":
    words = {"cat", "cart", "coat", "at"}
    expected = {"cot": ["cat", "coat"], "ca": ["cat"]}
    assert spelling_suggestions("Cot ca", words) == expected
