from typing import List, Tuple

def locate_least_variant_patch(grid: List[List[float]], size: int) -> Tuple[int, int]:
    h = len(grid) - size + 1
    w = len(grid[0]) - size + 1
    best_loc = (0, 0)
    min_variance = float("inf")
    for r in range(h):
        for c in range(w):
            patch_var = sum((grid[r + dr][c + dc] - 50.0)**2 for dr in range(size) for dc in range(size)) / float(size * size)
            if patch_var < min_variance:
                min_variance = patch_var
                best_loc = (r, c)
    return best_loc

if __name__ == "__main__":
    g = [[50.0]*4 for _ in range(4)]
    assert locate_least_variant_patch(g, 2) == (0, 0)
