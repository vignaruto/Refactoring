def nearest_values(pool: list[int], queries: list[int]) -> list[int]:
    answers = []
    for q in queries:
        best = pool[0]
        for candidate in pool:
            if abs(candidate - q) < abs(best - q):
                best = candidate
        answers.append(best)
    return answers

if __name__ == "__main__":
    assert nearest_values([1, 8, 15], [7, 12, 0]) == [8, 15, 1]
