def remove_isolated_pixels(img):
    h, w = len(img), len(img[0])
    out = [row[:] for row in img]
    for r in range(h):
        for c in range(w):
            if img[r][c] == 0:
                continue
            neighbours = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < h and 0 <= cc < w and img[rr][cc]:
                        neighbours += 1
            if neighbours == 0:
                out[r][c] = 0
    return out

if __name__ == "__main__":
    img = [[1, 0, 0], [0, 0, 0], [0, 1, 1]]
    assert remove_isolated_pixels(img) == [[0, 0, 0], [0, 0, 0], [0, 1, 1]]
