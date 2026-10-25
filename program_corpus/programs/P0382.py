def gamma_contrast_adjust(image: list[list[int]], gamma: float, low: int, high: int) -> list[list[int]]:
    adjusted = []
    for row in image:
        new_row = []
        for pixel in row:
            stretched = min(1.0, max(0.0, (pixel - low) / max(1, high - low)))
            new_row.append(int(round(255.0 * stretched ** gamma)))
        adjusted.append(new_row)
    return adjusted

if __name__ == "__main__":
    assert gamma_contrast_adjust([[0, 128, 255]], 1.0, 0, 255) == [[0, 128, 255]]
