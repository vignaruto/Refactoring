def upscale_double(img):
    h, w = len(img), len(img[0])
    out = [[0.0] * (2 * w - 1) for _ in range(2 * h - 1)]
    for r in range(2 * h - 1):
        for c in range(2 * w - 1):
            r0, c0 = r // 2, c // 2
            r1, c1 = min(r0 + r % 2, h - 1), min(c0 + c % 2, w - 1)
            out[r][c] = (img[r0][c0] + img[r0][c1] + img[r1][c0] + img[r1][c1]) / 4
    return out

if __name__ == "__main__":
    big = upscale_double([[0, 4], [8, 12]])
    assert big[0][1] == 2.0 and big[1][1] == 6.0 and big[2][2] == 12.0
