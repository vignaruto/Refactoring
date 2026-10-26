def next_sku_code(existing: list[str], prefix: str) -> str:
    highest = 0
    for code in existing:
        if not code.startswith(prefix + "-"):
            continue
        suffix = code[len(prefix) + 1:]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"{prefix}-{highest + 1:04d}"

if __name__ == "__main__":
    codes = ["TOOL-0007", "TOOL-0012", "PART-0099", "TOOL-x"]
    assert next_sku_code(codes, "TOOL") == "TOOL-0013"
    assert next_sku_code([], "BOLT") == "BOLT-0001"
