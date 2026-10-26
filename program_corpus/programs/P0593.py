def guess_caesar_shift(cipher):
    common = "etaoinshr"
    best_shift, best_score = 0, -1
    for shift in range(26):
        score = 0
        for ch in cipher.lower():
            if ch.isalpha():
                decoded = chr((ord(ch) - ord("a") - shift + 26) % 26 + ord("a"))
                score += 1 if decoded in common else 0
        if score > best_score:
            best_shift, best_score = shift, score
    return best_shift

if __name__ == "__main__":
    assert guess_caesar_shift("wkh vhfuhw lv qrw khuh") == 3
    assert guess_caesar_shift("the rain in spain") == 0
