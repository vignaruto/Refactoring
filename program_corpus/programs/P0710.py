def merge_contact(primary: dict, secondary: dict) -> dict:
    merged = dict(primary)
    for field, value in secondary.items():
        current = merged.get(field)
        if current is None or current == "" or isinstance(current, list) and not current:
            merged[field] = value
    return merged


if __name__ == "__main__":
    primary = {"name": "Ann", "phone": "", "tags": []}
    secondary = {"name": "A", "phone": "123", "tags": ["vip"]}
    secondary["email"] = "a@x.org"
    merged = merge_contact(primary, secondary)
    assert merged["name"] == "Ann"
    assert merged["phone"] == "123"
    assert merged["tags"] == ["vip"]
    assert merged["email"] == "a@x.org"
