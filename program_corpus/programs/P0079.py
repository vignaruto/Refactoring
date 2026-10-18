from typing import List

def apply_blur_filter(image: List[List[float]], kernel_weights: List[List[float]], divisor: float) -> List[List[float]]:
    h, w = len(image), len(image[0])
    filtered = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            filtered[r][c] = (image[r-1][c-1]*kernel_weights[0][0] + image[r-1][c]*kernel_weights[0][1] + image[r-1][c+1]*kernel_weights[0][2] + image[r][c-1]*kernel_weights[1][0] + image[r][c]*kernel_weights[1][1] + image[r][c+1]*kernel_weights[1][2] + image[r+1][c-1]*kernel_weights[2][0] + image[r+1][c]*kernel_weights[2][1] + image[r+1][c+1]*kernel_weights[2][2]) / divisor
    return filtered

if __name__ == "__main__":
    img = [[1.0]*3 for _ in range(3)]
    k = [[1.0]*3 for _ in range(3)]
    assert apply_blur_filter(img, k, 9.0)[1][1] == 1.0
