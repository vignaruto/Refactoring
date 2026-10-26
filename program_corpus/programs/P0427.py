import math

def gaussian_kernel_2d(size: int, sigma: float) -> list[list[float]]:
    half = size // 2
    kernel = []
    for y in range(-half, half + 1):
        row = []
        for x in range(-half, half + 1):
            row.append(math.exp(-(x * x + y * y) / (2.0 * sigma * sigma)) / (2.0 * math.pi * sigma * sigma))
        kernel.append(row)
    total = sum(sum(row) for row in kernel)
    return [[round(v / total, 4) for v in row] for row in kernel]

if __name__ == "__main__":
    k = gaussian_kernel_2d(3, 1.0)
    assert k[1][1] == max(map(max, k))
    assert abs(sum(map(sum, k)) - 1.0) < 1e-3
