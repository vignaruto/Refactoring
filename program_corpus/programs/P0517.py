def count_pair_sums(values: list[int], targets: list[int]) -> dict[int, int]:
    ordered = sorted(values)
    counts = {}
    for target in targets:
        i, j = 0, len(ordered) - 1
        found = 0
        while i < j and ordered[i] <= target and found < 10:
            pair = ordered[i] + ordered[j]
            if pair == target:
                found += 1
                i += 1
                j -= 1
            elif pair < target:
                i += 1
            else:
                j -= 1
        counts[target] = found
    return counts

if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5, 6]
    assert count_pair_sums(nums, [7, 3, 20]) == {7: 3, 3: 1, 20: 0}
