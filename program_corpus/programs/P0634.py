def expand_options(options):
    combos = [{}]
    for key in sorted(options):
        expanded = []
        for combo in combos:
            for value in options[key]:
                expanded.append({**combo, key: value})
        combos = expanded
    return combos

if __name__ == "__main__":
    options = {"size": ["S", "M"], "color": ["red"]}
    combos = expand_options(options)
    assert combos == [{"color": "red", "size": "S"}, {"color": "red", "size": "M"}]
