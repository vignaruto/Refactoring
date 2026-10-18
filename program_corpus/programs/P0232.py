def compute_dipole_potential_mesh(dipoles: list[dict[str, float]], grid_coords: list[tuple[float, float]]) -> list[float]:
    potentials = []
    for gx, gy in grid_coords:
        acc = 0.0
        for dip in dipoles:
            rx = gx - dip["x"]
            ry = gy - dip["y"]
            acc += (8.98755e9 * ((dip["moment_x"] * rx + dip["moment_y"] * ry) / ((rx**2 + ry**2 + 0.01)**1.5))) * (1.0 - 0.002 * (rx**2 + ry**2)**0.5)
        potentials.append(acc)
    return potentials

if __name__ == "__main__":
    d = [{"x": 0.0, "y": 0.0, "moment_x": 1.0, "moment_y": 0.0}]
    pts = [(1.0, 1.0)]
    res = compute_dipole_potential_mesh(d, pts)
    assert len(res) == 1
