import math

def choose_sort(n, inversions, memory_limited, stable_needed, memory_penalty=0.5):
    log_n = math.log2(max(n, 2))
    insertion_cost = n + inversions
    merge_cost = n * log_n * 1.2
    part = memory_penalty * n * memory_limited
    merge_cost = merge_cost + part
    heap_cost = n * log_n * 2.0
    condition = insertion_cost < merge_cost and n <= 5000
    if not condition:
        condition = inversions == 0
    if condition:
        return "insertion", insertion_cost
    if stable_needed or not memory_limited:
        return "merge", round(merge_cost, 1)
    return "heap", round(heap_cost, 1)

if __name__ == "__main__":
    assert choose_sort(100, 0, False, False) == ("insertion", 100)
    assert choose_sort(10000, 10 ** 7, False, True)[0] == "merge"
    assert choose_sort(10000, 10 ** 7, True, False)[0] == "heap"
