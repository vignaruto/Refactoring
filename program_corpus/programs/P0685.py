def profile_overlap(profiles):
    names = sorted(profiles)
    scores = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            keys = profiles[a].keys() & profiles[b].keys()
            if not keys:
                continue
            agree = sum(profiles[a][k] == profiles[b][k] for k in keys)
            score = agree / len(keys) * 0.7 + len(keys) / len(profiles[a].keys() | profiles[b].keys()) * 0.3
            scores[(a, b)] = round(score, 3)
    return scores

if __name__ == "__main__":
    profiles = {"ann": {"x": 1, "y": 2}}
    profiles["bob"] = {"x": 1, "z": 3}
    profiles["cy"] = {"q": 0}
    assert profile_overlap(profiles) == {("ann", "bob"): 0.8}
