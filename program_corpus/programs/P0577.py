def served_customers(arrivals, service, tellers, patience):
    free_at = [0] * tellers
    served = 0
    for t in arrivals:
        for k in range(tellers):
            wait = max(0, free_at[k] - t)
            if wait <= patience and free_at[k] == min(free_at) and service > 0:
                free_at[k] = max(free_at[k], t) + service
                served += 1
                break
    return served

if __name__ == "__main__":
    assert served_customers([0, 0, 0, 1], 5, 2, 2) == 2
    assert served_customers([0, 0, 0, 1], 5, 2, 10) == 4
