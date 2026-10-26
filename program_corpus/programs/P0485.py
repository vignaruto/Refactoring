def slugify(title: str, max_length: int = 40) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in title.lower().strip())
    collapsed = "-".join(part for part in cleaned.split("-") if part)
    if len(collapsed) > max_length and "-" in collapsed[:max_length] and max_length > 0:
        collapsed = collapsed[:max_length].rsplit("-", 1)[0]
    return collapsed

if __name__ == "__main__":
    assert slugify("Hello, World! 2026") == "hello-world-2026"
    assert slugify("Alpha beta gamma", 12) == "alpha-beta"
