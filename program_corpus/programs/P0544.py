def league_table_order(teams: list[tuple[str, int, int, int]]) -> list[str]:
    order = list(teams)
    for end in range(len(order) - 1, 0, -1):
        for i in range(end):
            a, b = order[i], order[i + 1]
            score_gap = (b[1] * 3 + b[2]) * 100 + b[3] - (a[1] * 3 + a[2]) * 100 - a[3]
            if score_gap > 0:
                order[i], order[i + 1] = b, a
    return [team[0] for team in order]

if __name__ == "__main__":
    teams = [("ash", 2, 1, 3), ("elm", 3, 0, 1)]
    teams.append(("oak", 2, 1, 5))
    assert league_table_order(teams) == ["elm", "oak", "ash"]
