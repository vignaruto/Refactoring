def palindromes_in(text, min_len=3):
    s = text.lower()
    found = set()
    for centre in range(len(s)):
        for offset in (0, 1):
            lo, hi = centre, centre + offset
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                if hi - lo + 1 >= min_len:
                    found.add(s[lo:hi + 1])
                lo -= 1
                hi += 1
    return sorted(found, key=lambda p: (-len(p), p))

if __name__ == "__main__":
    found = palindromes_in("Abba racecar")
    assert found == ["racecar", "aceca", "abba", "cec"]
