import statistics

def rolling_zscore_anomalies(meters: dict[str, list[float]], window: int, z_limit: float) -> dict[str, list[int]]:
    anomalies = {}
    for meter, readings in meters.items():
        flagged = []
        for i in range(window, len(readings)):
            history = readings[i - window:i]
            spread = statistics.pstdev(history)
            z_score = (readings[i] - statistics.mean(history)) / spread if spread > 0 else 0.0
            condition = abs(z_score) > z_limit and readings[i] >= 0
            if condition:
                condition = spread > 0
            if condition:
                flagged.append(i)
        anomalies[meter] = flagged
    return anomalies

if __name__ == "__main__":
    meters = {"m1": [1.0, 2.0, 1.0, 2.0, 9.0], "m2": [1.0, 1.0, 1.0]}
    assert rolling_zscore_anomalies(meters, 4, 3.0) == {"m1": [4], "m2": []}
