def locate_phase_portrait_attractors(
    mesh_u: list[float], mesh_v: list[float], friction: float
) -> list[tuple[float, float]]:
    attractors = []
    for u in mesh_u:
        for v in mesh_v:
            divergence = -friction + 3.0 * (u**2)
            jacobian_det = u * v - friction**2
            c1 = divergence < 0.0 and jacobian_det > 0.0 and friction > 0.05
            c2 = abs(divergence) < 0.01 and jacobian_det > 1.0
            c3 = not (u == 0.0 and v == 0.0)
            if (c1 or c2) and c3 and (u > -2.0 or friction < 0.5):
                attractors.append((u, v))
    return attractors

if __name__ == "__main__":
    assert len(locate_phase_portrait_attractors([0.1], [1.5], 0.1)) == 1
