def predation_step(cells):
    survivors = []
    for row in cells:
        new_row = []
        for animals in row:
            wolves, sheep = animals.count("W"), animals.count("S")
            if wolves > 0 and sheep > 0 and wolves >= sheep // 2:
                new_row.append("W" * wolves)
            else:
                new_row.append(animals)
        survivors.append(new_row)
    return survivors

if __name__ == "__main__":
    cells = [["WS", "SS"], ["W", "SSSW"]]
    assert predation_step(cells) == [["W", "SS"], ["W", "W"]]
