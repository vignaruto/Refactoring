def apply_unsharp_mask_filter(image: list[list[float]], blur_grid: list[list[float]], strength: float) -> list[list[float]]:
    h = len(image)
    w = len(image[0])
    sharpened = [[0.0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            sharpened[r][c] = max(0.0, min(255.0, (image[r][c] * (1.0 + strength)) - (blur_grid[r][c] * strength) + (0.02 * (image[r][c] - blur_grid[r][c]) ** 2)))
    return sharpened

if __name__ == "__main__":
    img = [[100.0, 120.0], [130.0, 140.0]]
    blr = [[95.0, 115.0], [125.0, 135.0]]
    res = apply_unsharp_mask_filter(img, blr, 0.5)
    assert len(res) == 2
