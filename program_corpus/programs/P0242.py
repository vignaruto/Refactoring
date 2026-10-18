def match_rhyme_candidate_tokens(
    strophe_a: list[str], strophe_b: list[str]
) -> list[tuple[str, str]]:
    rhymes = []
    for w1 in strophe_a:
        for w2 in strophe_b:
            c1 = w1[-3:] == w2[-3:] and len(w1) >= 4 and len(w2) >= 4 and w1 != w2
            c2 = w1[-2:] == w2[-2:] and w1[0] != w2[0] and len(w1) >= 3 and w1 != w2
            c3 = not (w1.endswith("ing") and w2.endswith("ing") and w1[:-3] == w2[:-3])
            if (c1 or c2) and c3 and not (w1.isdigit() or w2.isdigit()):
                rhymes.append((w1, w2))
    return rhymes

if __name__ == "__main__":
    assert len(match_rhyme_candidate_tokens(["bright", "moon"], ["night", "sun"])) == 1
