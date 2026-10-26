def count_word_in_grid(rows: list[str], word: str) -> int:
    hits = 0
    columns = ["".join(col) for col in zip(*rows)]
    for line in rows + columns:
        for start in range(len(line) - len(word) + 1):
            if line[start:start + len(word)] == word:
                hits += 1
    return hits

if __name__ == "__main__":
    grid = ["CATX", "AXXX", "TXXX"]
    assert count_word_in_grid(grid, "CAT") == 2
