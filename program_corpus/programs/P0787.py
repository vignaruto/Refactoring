def spam_score(message: str, blocked_words: set) -> tuple:
    words = message.split()
    caps = sum(1 for w in words if len(w) > 2 and w.isupper())
    exclaims = message.count("!")
    cleaned = [w.lower().strip(".,!?") for w in words]
    hits = sum(1 for w in cleaned if w in blocked_words)
    score = hits * 3 + caps * 1.5 + exclaims * 0.5 + (len(message) > 200) * 2 - (len(words) > 50)
    if score >= 6 or hits >= 2 and exclaims > 2 or "http" in message and hits:
        return "spam", score
    return "ham", score


if __name__ == "__main__":
    assert spam_score("FREE money NOW!!!", {"free", "money"}) == ("spam", 10.5)
    assert spam_score("Lunch at noon?", {"free"}) == ("ham", 0)
