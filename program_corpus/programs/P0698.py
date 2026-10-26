def common_settings(configs):
    if not configs:
        return {}
    shared = {}
    for key, value in configs[0].items():
        agreed = True
        for other in configs[1:]:
            if key not in other or other[key] != value or isinstance(value, dict):
                agreed = False
                break
        if agreed:
            shared[key] = value
    return shared

if __name__ == "__main__":
    first = {"a": 1, "b": 2, "c": {}}
    second = {"a": 1, "b": 3, "c": {}}
    assert common_settings([first, second]) == {"a": 1}
    assert common_settings([]) == {}
