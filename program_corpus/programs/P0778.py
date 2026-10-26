def windowed_correlation(xs, ys, window):
    out = []
    for start in range(len(xs) - window + 1):
        sx = sy = sxx = syy = sxy = 0.0
        for x, y in zip(xs[start:start + window], ys[start:start + window]):
            sx += x
            sy += y
            sxx += x * x
            syy += y * y
            sxy += x * y
        cov = sxy - sx * sy / window
        denom = ((sxx - sx * sx / window) * (syy - sy * sy / window)) ** 0.5
        out.append(round(cov / denom, 3) if denom else 0.0)
    return out

if __name__ == "__main__":
    assert windowed_correlation([1, 2, 3, 4], [2, 4, 6, 3], 3) == [1.0, -0.327]
