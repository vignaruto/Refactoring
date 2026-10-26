def filter_rows(rows: list[tuple], spec: dict[int, object], limit: int) -> list[tuple]:
    kept = []
    for row in rows:
        matches = all(row[i] == v for i, v in spec.items())
        if matches and len(kept) < limit and None not in row:
            kept.append(row)
    return kept

if __name__ == "__main__":
    rows = [(1, "a"), (2, "b"), (1, "b"), (1, None)]
    assert filter_rows(rows, {0: 1}, 5) == [(1, "a"), (1, "b")]
    assert filter_rows(rows, {0: 1}, 1) == [(1, "a")]
