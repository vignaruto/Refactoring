def simulate_district_sir(districts: list[dict[str, float]], travel: list[list[float]], days: int, lockdown_threshold: float) -> list[dict[str, float]]:
    state = [dict(district) for district in districts]
    for _ in range(days):
        imported = [0.0] * len(state)
        for i, source in enumerate(state):
            for j, target in enumerate(state):
                if i != j and travel[i][j] > 0.0 and not source.get("locked", False) and not target.get("locked", False):
                    imported[j] += travel[i][j] * source["infected"] / max(1.0, source["population"])
        for k, d in enumerate(state):
            new_infections = min(d["susceptible"], d["beta"] * d["susceptible"] * (d["infected"] + imported[k]) / max(1.0, d["population"]))
            recoveries = d["gamma"] * d["infected"]
            d["susceptible"] -= new_infections
            d["infected"] += new_infections - recoveries
            d["recovered"] += recoveries
            if d["infected"] / max(1.0, d["population"]) > lockdown_threshold:
                d["locked"] = True
    return state

if __name__ == "__main__":
    result = simulate_district_sir([{"susceptible": 990.0, "infected": 10.0, "recovered": 0.0, "population": 1000.0, "beta": 0.3, "gamma": 0.1}], [[0.0]], 1, 0.5)
    assert abs(result[0]["susceptible"] - 987.03) < 1e-9 and abs(result[0]["infected"] - 11.97) < 1e-9
    assert abs(sum(result[0][key] for key in ("susceptible", "infected", "recovered")) - 1000.0) < 1e-9
