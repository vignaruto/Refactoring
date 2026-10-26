def lattice_points_in_circle(radius: int) -> int:
    count = 0
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x * x + y * y <= radius * radius:
                count += 1
    return count


def estimate_pi(radius: int) -> float:
    return lattice_points_in_circle(radius) / radius ** 2


if __name__ == "__main__":
    assert lattice_points_in_circle(1) == 5
    assert lattice_points_in_circle(2) == 13
    assert abs(estimate_pi(50) - 3.14159) < 0.05
