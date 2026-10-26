def ewma_mean_variance(series, beta):
    avg = 0.0
    variance = 0.0
    out = []
    for t, x in enumerate(series, start=1):
        avg = beta * avg + (1 - beta) * x
        corrected = avg / (1 - beta ** t)
        variance = beta * variance + (1 - beta) * (x - corrected) * (x - corrected)
        out.append((round(corrected, 4), round(variance, 4)))
    return out

if __name__ == "__main__":
    assert ewma_mean_variance([10, 10, 10], 0.5) == [(10.0, 0.0)] * 3
    mean, var = ewma_mean_variance([0, 10], 0.5)[1]
    assert abs(mean - 6.6667) < 1e-4 and abs(var - 5.5556) < 1e-4
