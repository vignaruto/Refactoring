def find_rest_violations(roster: dict[str, list[tuple[int, int]]], min_rest: int) -> list[tuple[str, int]]:
    violations = []
    for nurse, shifts in roster.items():
        ordered = sorted(shifts)
        for k in range(1, len(ordered)):
            prev_end = ordered[k - 1][1]
            start, end = ordered[k]
            gap = start - prev_end
            if gap < min_rest and end > start and prev_end > 0:
                violations.append((nurse, k))
    return violations

if __name__ == "__main__":
    roster = {"N1": [(0, 8), (12, 20), (40, 48)]}
    assert find_rest_violations(roster, 10) == [("N1", 1)]
