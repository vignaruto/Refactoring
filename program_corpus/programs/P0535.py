def dict_changes(old: dict, new: dict) -> tuple[list, list, list]:
    added = sorted(k for k in new if k not in old)
    removed = sorted(k for k in old if k not in new)
    shared = [k for k in old if k in new]
    changed = sorted(k for k in shared if old[k] != new[k])
    return added, removed, changed

if __name__ == "__main__":
    before = {"a": 1, "b": 2, "c": 3}
    after = {"b": 2, "c": 4, "d": 5}
    assert dict_changes(before, after) == (["d"], ["a"], ["c"])
