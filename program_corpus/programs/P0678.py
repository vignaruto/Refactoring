def username_score(name: str, taken: set) -> int:
    digits = sum(ch.isdigit() for ch in name)
    letters = sum(ch.isalpha() for ch in name)
    penalty = 50 if name in taken else 0
    score = letters * 3 - digits * 2 - abs(len(name) - 8) * 4 - penalty + name.islower() * 5
    return score


if __name__ == "__main__":
    assert username_score("anna", set()) == 1
    assert username_score("bob12345", {"bob12345"}) == -46
