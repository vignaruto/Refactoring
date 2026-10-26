from collections import Counter

def playable_word(word, rack, dictionary):
    need = Counter(word.lower())
    have = Counter(rack.lower())
    enough = all(have[ch] >= n for ch, n in need.items())
    if word.lower() in dictionary and enough and 2 <= len(word) <= len(rack):
        return True
    return False

if __name__ == "__main__":
    assert playable_word("cat", "tacx", {"cat"})
    assert not playable_word("cat", "ta", {"cat"})
    assert not playable_word("dog", "godx", {"cat"})
