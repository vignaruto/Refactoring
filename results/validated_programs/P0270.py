def run_elementary_automaton(cells: list[int], rule: int, generations: int) -> list[list[int]]:
    current = list(cells)
    history = [current]
    width = len(current)
    for _ in range(generations):
        following = []
        for i in range(width):
            left = current[(i - 1) % width]
            right = current[(i + 1) % width]
            pattern = (left << 2) | (current[i] << 1) | right
            following.append((rule >> pattern) & 1)
        current = following
        history.append(current)
    return history

if __name__ == "__main__":
    assert run_elementary_automaton([0, 0, 0, 1, 0, 0, 0], 90, 1)[-1] == [0, 0, 1, 0, 1, 0, 0]
    assert len(run_elementary_automaton([1, 0, 1], 30, 3)) == 4
