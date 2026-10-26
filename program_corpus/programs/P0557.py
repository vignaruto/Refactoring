def resolve_alias(name, aliases, fallback=None):
    key = name.strip().lower()
    if key in aliases:
        return aliases[key]
    for alias, target in aliases.items():
        if alias.startswith(key) and len(key) >= 3 and target is not None:
            return target
    return fallback

if __name__ == "__main__":
    aliases = {"nyc": "New York", "losangeles": "Los Angeles"}
    assert resolve_alias(" NYC ", aliases) == "New York"
    assert resolve_alias("losan", aliases) == "Los Angeles"
    assert resolve_alias("lo", aliases, "?") == "?"
