def near_matches(word, dictionary):
    matches = []
    for candidate in dictionary:
        if abs(len(candidate) - len(word)) > 1:
            continue
        i = j = edits = 0
        while i < len(word) and j < len(candidate) and edits <= 1:
            if word[i] == candidate[j]:
                i += 1
                j += 1
                continue
            edits += 1
            if len(word) > len(candidate):
                i += 1
            elif len(candidate) > len(word):
                j += 1
            else:
                i += 1
                j += 1
        if edits + len(word) - i + len(candidate) - j == 1:
            matches.append(candidate)
    return matches

if __name__ == "__main__":
    words = ["cat", "cot", "cast", "at", "dog", "cats"]
    assert near_matches("cat", words) == ["cot", "cast", "at", "cats"]
