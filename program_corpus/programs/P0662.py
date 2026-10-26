def cross_tab(rows, row_key, col_key):
    row_labels = sorted({r[row_key] for r in rows})
    col_labels = sorted({r[col_key] for r in rows})
    table = {a: {b: 0 for b in col_labels} for a in row_labels}
    for record in rows:
        table[record[row_key]][record[col_key]] += 1
    return table


def row_shares(table):
    shares = {}
    for a, counts in table.items():
        total = sum(counts.values())
        for b, n in counts.items():
            shares[(a, b)] = round(n / total, 3) if total else 0.0
    return shares


if __name__ == "__main__":
    rows = [{"g": "x", "r": "yes"}, {"g": "x", "r": "no"}]
    rows.append({"g": "y", "r": "yes"})
    table = cross_tab(rows, "g", "r")
    assert table == {"x": {"no": 1, "yes": 1}, "y": {"no": 0, "yes": 1}}
    assert row_shares(table)[("x", "yes")] == 0.5
