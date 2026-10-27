import itertools

def minesweeper_hints(board: list[str]) -> list[str]:
    rows, cols = len(board), len(board[0])
    output = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            if board[r][c] == "*":
                line += "*"
                continue
            count = 0
            for dr, dc in itertools.product((-1, 0, 1), (-1, 0, 1)):
                nr, nc = r + dr, c + dc
                condition = 0 <= nr < rows and 0 <= nc < cols
                if condition:
                    condition = board[nr][nc] == '*'
                if condition:
                    count += 1
            line += str(count) if count else "."
        output.append(line)
    return output

if __name__ == "__main__":
    assert minesweeper_hints(["*..", "...", "..*"]) == ["*1.", "121", ".1*"]
