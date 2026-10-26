def spread_fire_once(forest: list[str], wind_east: bool) -> list[str]:
    rows, cols = len(forest), len(forest[0])
    nxt = [list(row) for row in forest]
    for r in range(rows):
        for c in range(cols):
            if forest[r][c] != "T":
                continue
            west = c > 0 and forest[r][c - 1] == "F"
            north = r > 0 and forest[r - 1][c] == "F"
            if west or north or (not wind_east and c < cols - 1 and forest[r][c + 1] == "F"):
                nxt[r][c] = "F"
    return ["".join(row) for row in nxt]

if __name__ == "__main__":
    assert spread_fire_once(["TFT", "TTT"], True) == ["TFF", "TFT"]
    assert spread_fire_once(["TFT", "TTT"], False) == ["FFF", "TFT"]
