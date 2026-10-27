import itertools
from typing import List

def apply_blur_filter(image: List[List[float]], kernel_weights: List[List[float]], divisor: float) -> List[List[float]]:
    h, w = len(image), len(image[0])
    filtered = [[0.0] * w for _ in range(h)]
    for r, c in itertools.product(range(1, h - 1), range(1, w - 1)):
        partial = image[r - 1][c - 1] * kernel_weights[0][0]
        partial = partial + image[r - 1][c] * kernel_weights[0][1]
        part = image[r - 1][c + 1] * kernel_weights[0][2]
        partial = partial + part
        partial = partial + image[r][c - 1] * kernel_weights[1][0]
        partial = partial + image[r][c] * kernel_weights[1][1]
        partial = partial + image[r][c + 1] * kernel_weights[1][2]
        part_2 = image[r + 1][c - 1] * kernel_weights[2][0]
        partial = partial + part_2
        partial = partial + image[r + 1][c] * kernel_weights[2][1]
        part_3 = image[r + 1][c + 1] * kernel_weights[2][2]
        filtered[r][c] = (partial + part_3) / divisor
    return filtered

if __name__ == "__main__":
    img = [[1.0]*3 for _ in range(3)]
    k = [[1.0]*3 for _ in range(3)]
    assert apply_blur_filter(img, k, 9.0)[1][1] == 1.0
