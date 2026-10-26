def gantt_rows(tasks, horizon):
    rows = []
    for name, start, length in tasks:
        cells = []
        for hour in range(horizon):
            cells.append("#" if start <= hour < start + length else ".")
        bar = "".join(cells)
        rows.append(f"{name:<6}{bar}")
    return rows

if __name__ == "__main__":
    rows = gantt_rows([("cut", 1, 2), ("sew", 2, 3)], 6)
    assert rows == ["cut   .##...", "sew   ..###."]
