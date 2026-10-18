def snake_to_camel(identifier: str) -> str:
    tokens = identifier.strip().split("_")
    filtered = [token for token in tokens if token]
    if not filtered:
        return ""
    lead = filtered[0].lower()
    tail = [word.capitalize() for word in filtered[1:]]
    return lead + "".join(tail)

if __name__ == "__main__":
    assert snake_to_camel("order_unit_cost") == "orderUnitCost"
