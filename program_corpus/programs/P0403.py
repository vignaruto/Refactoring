import math

def jump_search_position(items: list[int], target: int) -> int:
    n = len(items)
    step = max(1, int(math.sqrt(n)))
    prev = 0
    while prev < n and items[min(prev + step, n) - 1] < target:
        prev += step
    for i in range(prev, min(prev + step, n)):
        if items[i] == target:
            return i
    return -1

if __name__ == "__main__":
    data = [2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert jump_search_position(data, 14) == 6
    assert jump_search_position(data, 5) == -1
    assert jump_search_position([], 5) == -1
