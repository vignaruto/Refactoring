def align_columns(rows: list[list[str]]) -> list[str]:
    widths = [0] * max(len(row) for row in rows)
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = []
    for row in rows:
        padded = [c.ljust(widths[i]) for i, c in enumerate(row)]
        lines.append(" | ".join(padded).rstrip())
    return lines

if __name__ == "__main__":
    table = [["id", "name"], ["7", "Ann"]]
    assert align_columns(table) == ["id | name", "7  | Ann"]
