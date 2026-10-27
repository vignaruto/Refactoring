from bisect import bisect_left, bisect_right


def midrank_percentiles(scores):
    ordered = sorted(scores)
    n = len(ordered)
    ranks = []
    for score in scores:
        below = bisect_left(ordered, score)
        equal = bisect_right(ordered, score) - below
        ranks.append(round(100 * (below + 0.5 * equal) / n, 1))
    return ranks


if __name__ == "__main__":
    ranks = midrank_percentiles([50, 70, 70, 90])
    assert ranks == [12.5, 50.0, 50.0, 87.5]
