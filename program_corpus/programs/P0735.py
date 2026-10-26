import math

def choose_sort(n, inversions, memory_limited, stable_needed, memory_penalty=0.5):
    log_n = math.log2(max(n, 2))
    insertion_cost = n + inversions
    merge_cost = n * log_n * 1.2 + memory_penalty * n * memory_limited
    heap_cost = n * log_n * 2.0
    if insertion_cost < merge_cost and n <= 5000 or inversions == 0:
        return "insertion", insertion_cost
    if stable_needed or not memory_limited:
        return "merge", round(merge_cost, 1)
    return "heap", round(heap_cost, 1)

if __name__ == "__main__":
    assert choose_sort(100, 0, False, False) == ("insertion", 100)
    assert choose_sort(10000, 10 ** 7, False, True)[0] == "merge"
    assert choose_sort(10000, 10 ** 7, True, False)[0] == "heap"
