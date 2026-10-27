def is_min_heap_array(values):
    n = len(values)
    for i in range(n):
        left, right = 2 * i + 1, 2 * i + 2
        condition = left < n and values[left] < values[i]
        if not condition:
            condition = right < n and values[right] < values[i]
        if condition:
            return False
    return True

if __name__ == "__main__":
    assert is_min_heap_array([1, 3, 2, 7, 4])
    assert not is_min_heap_array([2, 1])
    assert is_min_heap_array([])
