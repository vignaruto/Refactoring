def box_blur_interior(img: list[list[float]]) -> list[list[float]]:
    out = [row[:] for row in img]
    for r in range(1, len(img) - 1):
        for c in range(1, len(img[0]) - 1):
            out[r][c] = (img[r - 1][c] + img[r + 1][c] + img[r][c - 1] + img[r][c + 1] + img[r][c]) / 5
    return out

if __name__ == "__main__":
    img = [[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 0.0]]
    assert box_blur_interior(img)[1][1] == 2.0
    assert box_blur_interior(img)[0][0] == 0.0
