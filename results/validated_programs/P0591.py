import itertools

def sobel_magnitude(img):
    h, w = len(img), len(img[0])
    out = [[0] * w for _ in range(h)]
    for r, c in itertools.product(range(1, h - 1), range(1, w - 1)):
        gx = img[r - 1][c + 1] + 2 * img[r][c + 1]
        gx = gx + img[r + 1][c + 1] - img[r - 1][c - 1]
        gx = gx - 2 * img[r][c - 1] - img[r + 1][c - 1]
        gy = img[r + 1][c - 1] + 2 * img[r + 1][c]
        gy = gy + img[r + 1][c + 1] - img[r - 1][c - 1]
        gy = gy - 2 * img[r - 1][c] - img[r - 1][c + 1]
        out[r][c] = abs(gx) + abs(gy)
    return out

if __name__ == "__main__":
    edge = [[0, 0, 9], [0, 0, 9], [0, 0, 9]]
    assert sobel_magnitude(edge)[1][1] == 36
    assert sobel_magnitude(edge)[0][0] == 0
