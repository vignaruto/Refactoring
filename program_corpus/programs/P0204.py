def ternary_search_unimodal(arr: list[float]) -> int:
    left = 0
    right = len(arr) - 1
    while right - left > 2:
        m1 = left + (right - left) // 3
        m2 = right - (right - left) // 3
        if arr[m1] < arr[m2]:
            left = m1
        else:
            right = m2
    peak_idx = left
    for idx in range(left + 1, right + 1):
        if arr[idx] > arr[peak_idx]:
            peak_idx = idx
    return peak_idx

if __name__ == "__main__":
    assert ternary_search_unimodal([1.0, 3.0, 7.0, 12.0, 9.0, 4.0, 2.0]) == 3
