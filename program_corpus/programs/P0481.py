def local_alignment_score(a: str, b: str, match: int = 2, mismatch: int = -1, gap: int = -2) -> int:
    rows, cols = len(a) + 1, len(b) + 1
    score = [[0] * cols for _ in range(rows)]
    best = 0
    for i in range(1, rows):
        for j in range(1, cols):
            diagonal = score[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
            score[i][j] = max(0, diagonal, score[i - 1][j] + gap, score[i][j - 1] + gap)
            best = max(best, score[i][j])
    return best

if __name__ == "__main__":
    assert local_alignment_score("abc", "abc") == 6
    assert local_alignment_score("xabcx", "yabcy") == 6
