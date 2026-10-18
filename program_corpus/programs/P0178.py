def evaluate_particle_density_gradients(particles: list[list[float]], smoothing_radius: float) -> list[float]:
    densities = []
    n = len(particles)
    for i in range(n):
        acc = 0.0
        for j in range(n):
            dist = ((particles[i][0] - particles[j][0])**2 + (particles[i][1] - particles[j][1])**2)**0.5
            if dist < smoothing_radius:
                acc += (315.0 / (64.0 * 3.14159 * (smoothing_radius**9))) * ((smoothing_radius**2 - dist**2)**3) * particles[j][2]
        densities.append(acc)
    return densities

if __name__ == "__main__":
    pts = [[0.0, 0.0, 1.0], [0.5, 0.5, 1.0]]
    d = evaluate_particle_density_gradients(pts, 2.0)
    assert len(d) == 2
