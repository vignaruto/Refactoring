def lattice_points_in_ring(inner: int, outer: int) -> int:
    count = 0
    for x in range(-outer, outer + 1):
        for y in range(-outer, outer + 1):
            dist = x * x + y * y
            if inner * inner <= dist <= outer * outer and (x + y) % 2 == 0:
                count += 1
    return count

if __name__ == "__main__":
    assert lattice_points_in_ring(1, 2) == 8
    assert lattice_points_in_ring(1, 1) == 0
