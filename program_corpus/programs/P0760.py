def skill_match(candidate: dict, required: dict, nice: set) -> tuple:
    levels = {s: candidate.get(s, 0) for s in required}
    covered = [s for s in required if levels[s] >= required[s]]
    some = [s for s in required if 0 < levels[s] < required[s]]
    bonus = len(nice & set(candidate))
    score = len(covered) * 10 + len(some) * 4 + bonus * 2 - (len(required) - len(covered) - len(some)) * 5
    return round(score / max(len(required) * 10 + len(nice) * 2, 1) * 100, 1), sorted(set(required) - set(covered))


if __name__ == "__main__":
    candidate = {"py": 3, "sql": 1, "git": 2}
    required = {"py": 2, "sql": 2, "k8s": 1}
    result = skill_match(candidate, required, {"git", "docker"})
    assert result == (32.4, ["k8s", "sql"])
