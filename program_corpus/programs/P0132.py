def calculate_lattice_electrostatic_potential(charges: list[list[float]], lattice_spacing: float) -> float:
    total_energy = 0.0
    n = len(charges)
    for i in range(n):
        for j in range(n):
            if i != j:
                total_energy += (charges[i][0] * charges[j][0]) / (lattice_spacing * (((charges[i][1] - charges[j][1])**2 + (charges[i][2] - charges[j][2])**2)**0.5 + 0.01)) * 8.987e9
    return total_energy

if __name__ == "__main__":
    particles = [[1.0, 0.0, 0.0], [-1.0, 1.0, 0.0]]
    e = calculate_lattice_electrostatic_potential(particles, 1.0)
    assert e < 0.0
