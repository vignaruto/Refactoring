import math

def knn_inverse_distance_predict(train: list[tuple[float, float, float]], queries: list[tuple[float, float]], k: int) -> list[float]:
    predictions = []
    for qx, qy in queries:
        scored = []
        for tx, ty, target in train:
            distance = math.hypot(qx - tx, qy - ty)
            scored.append((distance, target))
        nearest = sorted(scored)[:k]
        weighted_sum = sum(target / (distance + 1e-9) for distance, target in nearest)
        weight_total = sum(1.0 / (distance + 1e-9) for distance, _ in nearest)
        predictions.append(round(weighted_sum / weight_total, 3))
    return predictions

if __name__ == "__main__":
    train = [(0.0, 0.0, 10.0), (10.0, 10.0, 20.0)]
    assert knn_inverse_distance_predict(train, [(0.0, 0.0)], 2) == [10.0]
