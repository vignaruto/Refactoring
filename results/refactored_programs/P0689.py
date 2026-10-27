def interpolation_lookup(sorted_values, queries):
    results = {}
    for query in queries:
        lo, hi = 0, len(sorted_values) - 1
        results[query] = -1
        while lo <= hi and sorted_values[lo] <= query <= sorted_values[hi]:
            if sorted_values[hi] == sorted_values[lo]:
                probe = lo
            else:
                probe = lo
                part = (query - sorted_values[lo]) * (hi - lo)
                part = part // (sorted_values[hi] - sorted_values[lo])
                probe = probe + part
            if sorted_values[probe] == query:
                results[query] = probe
                break
            if sorted_values[probe] < query:
                lo = probe + 1
            else:
                hi = probe - 1
    return results

if __name__ == "__main__":
    values = [2, 4, 8, 16, 32, 64]
    found = interpolation_lookup(values, [16, 5, 2, 64])
    assert found == {16: 3, 5: -1, 2: 0, 64: 5}
