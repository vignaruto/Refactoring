def pert_estimate(tasks):
    total_mean = 0.0
    total_var = 0.0
    for optimistic, most_likely, pessimistic in tasks:
        expected_duration = (optimistic + 4 * most_likely + pessimistic) / 6
        total_mean += expected_duration
        total_var += ((pessimistic - optimistic) / 6) ** 2
    return round(total_mean, 2), round(total_var ** 0.5, 2), round(total_mean + 1.645 * total_var ** 0.5, 2)

if __name__ == "__main__":
    tasks = [(2, 4, 6), (1, 2, 9)]
    assert pert_estimate(tasks) == (7.0, 1.49, 9.45)
