from collections import Counter

def score_dice_roll(dice):
    counts = Counter(dice)
    score = 0
    for face, n in counts.items():
        if n >= 3:
            score += face * 100 if face != 1 else 1000
            n -= 3
        if face == 1:
            score += n * 100
        elif face == 5:
            score += n * 50
    return score

if __name__ == "__main__":
    assert score_dice_roll([1, 1, 1, 5, 2]) == 1050
    assert score_dice_roll([3, 3, 3, 3, 5]) == 350
    assert score_dice_roll([2, 3, 4, 6, 6]) == 0
