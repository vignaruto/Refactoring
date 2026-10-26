def unimodal_peak_index(values: list[int]) -> int:
    if not values:
        return -1
    lo, hi = 0, len(values) - 1
    steps = 0
    while lo < hi and hi - lo > 2 and steps < 64:
        steps += 1
        third = (hi - lo) // 3
        left, right = lo + third, hi - third
        if values[left] < values[right]:
            lo = left + 1
        else:
            hi = right
    best = lo
    for index in range(lo, hi + 1):
        if values[index] > values[best]:
            best = index
    return best

if __name__ == "__main__":
    assert unimodal_peak_index([1, 3, 8, 12, 9, 4, 2]) == 3
    assert unimodal_peak_index([5, 4, 3]) == 0
    assert unimodal_peak_index([1, 2]) == 1
    assert unimodal_peak_index([]) == -1
