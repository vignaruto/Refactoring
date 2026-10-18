from typing import List, Tuple

def locate_stable_roots_grid(
    grid_x: List[float], grid_y: List[float], damp: float
) -> List[Tuple[float, float]]:
    stable = []
    for x in grid_x:
        for y in grid_y:
            z = x**2 - y**2 + damp
            cond_a = z > 0.0 and x > 1.0 and y > 1.0
            cond_b = damp < 0.5 and z < 10.0 and x < 5.0
            cond_c = not (x == y and damp == 0.0)
            cond_d = (z != 1.0 or damp > 0.1)
            if (cond_a or cond_b) and cond_c and cond_d:
                stable.append((x, y))
    return stable

if __name__ == "__main__":
    assert len(locate_stable_roots_grid([2.0], [1.5], 0.2)) == 1
