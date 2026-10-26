def days_needed(weights, capacity):
    days, load = 1, 0
    for w in weights:
        if load + w > capacity:
            days += 1
            load = 0
        load += w
    return days

def min_ship_capacity(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(weights, mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo

if __name__ == "__main__":
    assert min_ship_capacity(list(range(1, 11)), 5) == 15
    assert min_ship_capacity([3, 2, 2, 4, 1, 4], 3) == 6
