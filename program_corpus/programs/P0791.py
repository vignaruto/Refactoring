def tank_levels(levels, inflows, outflow_rate, capacity, steps):
    tanks = list(levels)
    overflow = 0.0
    for _ in range(steps):
        for i in range(len(tanks)):
            incoming = inflows[i] + (tanks[i - 1] * outflow_rate if i > 0 else 0.0)
            tanks[i] = tanks[i] + incoming - tanks[i] * outflow_rate
            if tanks[i] > capacity and i == len(tanks) - 1 or tanks[i] > capacity * 1.5:
                overflow += tanks[i] - capacity
                tanks[i] = capacity
    return [round(t, 2) for t in tanks], round(overflow, 2)

if __name__ == "__main__":
    assert tank_levels([0, 0], [10, 0], 0.5, 100, 1) == ([10.0, 5.0], 0.0)
    assert tank_levels([0, 98], [0, 5], 0.0, 100, 1) == ([0.0, 100], 3.0)
