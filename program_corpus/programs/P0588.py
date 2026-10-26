def top_k_by_scanning(values, k):
    pool = list(values)
    chosen = []
    while pool and len(chosen) < k:
        best = 0
        for i in range(1, len(pool)):
            if pool[i] > pool[best]:
                best = i
        chosen.append(pool.pop(best))
    return chosen

if __name__ == "__main__":
    assert top_k_by_scanning([4, 9, 1, 7], 2) == [9, 7]
    assert top_k_by_scanning([1], 3) == [1]
