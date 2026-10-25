def find_active_mutual_follows(follows: dict[str, list[str]], active: dict[str, bool]) -> list[tuple[str, str]]:
    pairs = []
    for user, followed in follows.items():
        for other in followed:
            if user < other and user in follows.get(other, []) and active.get(user) and active.get(other):
                pairs.append((user, other))
    return sorted(pairs)

if __name__ == "__main__":
    assert find_active_mutual_follows({"a": ["b", "c"], "b": ["a"], "c": ["a"], "d": ["a"]}, {"a": True, "b": True, "c": False}) == [("a", "b")]
