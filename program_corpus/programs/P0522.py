def shared_tags(groups: list[list[str]], banned: set[str]) -> list[str]:
    seen_in = {}
    for index, group in enumerate(groups):
        for tag in set(group):
            clean = tag.strip().lower()
            if clean and clean not in banned and not clean.startswith("#"):
                seen_in.setdefault(clean, set()).add(index)
    common = [t for t, ids in seen_in.items() if len(ids) > 1]
    return sorted(common)

if __name__ == "__main__":
    groups = [["Red", "blue"], ["red ", "#x"]]
    groups.append(["BLUE", "green"])
    assert shared_tags(groups, {"green"}) == ["blue", "red"]
    assert shared_tags(groups, {"red", "blue"}) == []
