import math

def bilateral_filter_1d(signal: list[float], sigma_spatial: float, sigma_range: float) -> list[float]:
    n = len(signal)
    smoothed = []
    for i in range(n):
        num = 0.0
        den = 0.0
        for j in range(n):
            weight = math.exp(-((i - j) ** 2) / (2.0 * sigma_spatial ** 2) - ((signal[i] - signal[j]) ** 2) / (2.0 * sigma_range ** 2))
            num += weight * signal[j]
            den += weight
        smoothed.append(round(num / den, 4))
    return smoothed

if __name__ == "__main__":
    out = bilateral_filter_1d([1.0, 1.0, 10.0, 10.0], 1.0, 0.5)
    assert out[0] < 1.1 and out[3] > 9.9
