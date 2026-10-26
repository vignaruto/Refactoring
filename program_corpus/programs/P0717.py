from itertools import combinations


def co_occurrence(baskets):
    pairs = {}
    for basket in baskets:
        for a, b in combinations(sorted(set(basket)), 2):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return pairs


def pair_lift(pairs, baskets, a, b):
    n = len(baskets)
    count_a = sum(a in basket for basket in baskets)
    count_b = sum(b in basket for basket in baskets)
    ratio = pairs.get((min(a, b), max(a, b)), 0) * n / max(count_a * count_b, 1)
    return round(ratio, 3)


if __name__ == "__main__":
    baskets = [["milk", "bread"], ["milk", "eggs"]]
    baskets.append(["bread", "milk"])
    baskets.append(["eggs"])
    pairs = co_occurrence(baskets)
    assert pairs == {("bread", "milk"): 2, ("eggs", "milk"): 1}
    assert pair_lift(pairs, baskets, "milk", "bread") == 1.333
    assert pair_lift(pairs, baskets, "eggs", "milk") == 0.667
