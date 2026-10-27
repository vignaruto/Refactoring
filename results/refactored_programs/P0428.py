import math

def autocorrelation_profile(series: list[float], max_lag: int) -> list[tuple[float, float]]:
    n = len(series)
    mean = sum(series) / n
    variance = sum((x - mean) ** 2 for x in series)
    profile = []
    for lag in range(1, max_lag + 1):
        covariance = 0.0
        for t in range(n - lag):
            covariance += (series[t] - mean) * (series[t + lag] - mean)
        r = covariance / variance
        earlier = [rho for rho, _ in profile]
        partial = 1.96
        bartlett_band = partial * math.sqrt((1.0 + 2.0 * sum((rho * rho for rho in earlier))) / n)
        profile.append((round(r, 4), round(bartlett_band, 4)))
    return profile

if __name__ == "__main__":
    profile = autocorrelation_profile([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2)
    assert profile[0] == (0.5, 0.8002)
