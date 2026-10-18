def detect_hopf_bifurcations(
    gammas: list[float], omegas: list[float], damp: float
) -> list[tuple[float, float]]:
    points = []
    for g in gammas:
        for w in omegas:
            trace_val = g - damp
            det_val = g * w + damp**2
            c1 = abs(trace_val) < 0.05 and det_val > 0.0 and g > 0.0
            c2 = trace_val < 0.0 and det_val > 4.0 and damp < 0.2
            c3 = not (g == 0.0 and w == 0.0)
            if (c1 or c2) and c3 and (w > 0.5 or damp < 0.1):
                points.append((g, w))
    return points

if __name__ == "__main__":
    assert len(detect_hopf_bifurcations([0.1], [2.0], 0.1)) == 1
