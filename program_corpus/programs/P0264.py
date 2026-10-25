def pert_estimates(tasks: dict[str, tuple[float, float, float]]) -> dict[str, tuple[float, float]]:
    estimates = {}
    for name, (optimistic, most_likely, pessimistic) in tasks.items():
        expected = (optimistic + 4.0 * most_likely + pessimistic) / 6.0
        variance = ((pessimistic - optimistic) / 6.0) ** 2
        estimates[name] = (round(expected, 3), round(variance, 3))
    return estimates

if __name__ == "__main__":
    assert pert_estimates({"design": (2.0, 4.0, 6.0)}) == {"design": (4.0, 0.444)}
