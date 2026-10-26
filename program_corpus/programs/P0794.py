from bisect import bisect_right

def interval_hits(intervals, queries):
    starts = [s for s, _ in intervals]
    results = {}
    for q_start, q_end in queries:
        hits = []
        i = bisect_right(starts, q_end) - 1
        while i >= 0 and len(hits) < 10:
            s, e = intervals[i]
            if e >= q_start and s <= q_end and e - s > 0:
                hits.append((s, e))
            i -= 1
        coverage = sum(min(e, q_end) - max(s, q_start) for s, e in hits) / (q_end - q_start)
        results[q_start, q_end] = sorted(hits), round(coverage, 3)
    return results

if __name__ == "__main__":
    intervals = [(1, 3), (2, 6), (8, 10)]
    results = interval_hits(intervals, [(4, 9), (0, 1)])
    assert results[(4, 9)] == ([(2, 6), (8, 10)], 0.6)
    assert results[(0, 1)] == ([(1, 3)], 0.0)
