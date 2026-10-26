def bounce_particles(positions: list[float], velocities: list[float], width: float, steps: int) -> list[float]:
    pos = list(positions)
    vel = list(velocities)
    for _ in range(steps):
        for i in range(len(pos)):
            pos[i] += vel[i]
            if pos[i] < 0.0 or pos[i] > width:
                vel[i] = -vel[i]
                pos[i] = max(0.0, min(width, pos[i]))
    return pos

if __name__ == "__main__":
    assert bounce_particles([1.0], [2.0], 4.0, 3) == [2.0]
