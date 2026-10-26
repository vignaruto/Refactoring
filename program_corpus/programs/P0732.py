def distanced_seats(seats):
    good = []
    for r, row in enumerate(seats):
        for c, seat in enumerate(row):
            left_free = c == 0 or row[c - 1] == "."
            right_free = c == len(row) - 1 or row[c + 1] == "."
            if seat == "." and left_free and right_free:
                good.append((r, c))
    return good

if __name__ == "__main__":
    seats = ["..X.", "...."]
    expected = [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
    assert distanced_seats(seats) == expected
