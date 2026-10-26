def teller_finish_times(service_times: list[int], tellers: int) -> list[int]:
    free_at = [0] * tellers
    finishes = []
    for duration in service_times:
        best = 0
        for t in range(1, tellers):
            if free_at[t] < free_at[best]:
                best = t
        free_at[best] += duration
        finishes.append(free_at[best])
    return finishes

if __name__ == "__main__":
    assert teller_finish_times([5, 3, 2, 4], 2) == [5, 3, 5, 9]
