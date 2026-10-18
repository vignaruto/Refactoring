import math

def compute_sobel_gradient_energy(raster: list[list[float]]) -> list[list[float]]:
    h = len(raster)
    w = len(raster[0])
    energy = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            energy[r][c] = math.sqrt(((raster[r-1][c+1] + 2*raster[r][c+1] + raster[r+1][c+1]) - (raster[r-1][c-1] + 2*raster[r][c-1] + raster[r+1][c-1]))**2 + ((raster[r+1][c-1] + 2*raster[r+1][c] + raster[r+1][c+1]) - (raster[r-1][c-1] + 2*raster[r-1][c] + raster[r-1][c+1]))**2)
    return energy

if __name__ == "__main__":
    img = [[0.0]*3 for _ in range(3)]
    res = compute_sobel_gradient_energy(img)
    assert len(res) == 3
