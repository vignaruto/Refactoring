def elementary_automaton(cells, rule, generations):
    history = [list(cells)]
    for _ in range(generations):
        row = history[-1]
        nxt = []
        for i in range(len(row)):
            left = row[i - 1] if i > 0 else 0
            right = row[i + 1] if i < len(row) - 1 else 0
            index = left * 4 + row[i] * 2 + right
            nxt.append((rule >> index) & 1)
        history.append(nxt)
    return history

if __name__ == "__main__":
    history = elementary_automaton([0, 0, 1, 0, 0], 90, 2)
    assert history[1] == [0, 1, 0, 1, 0]
    assert history[2] == [1, 0, 0, 0, 1]
