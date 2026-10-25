import math

def mean_silhouette_score(points: list[tuple[float, float]], labels: list[int]) -> float:
    scores = []
    for i, p in enumerate(points):
        same, other = [], {}
        for j, q in enumerate(points):
            if i == j:
                continue
            distance = math.hypot(p[0] - q[0], p[1] - q[1])
            if labels[j] == labels[i]:
                same.append(distance)
            else:
                other.setdefault(labels[j], []).append(distance)
        if not same or not other:
            scores.append(0.0)
            continue
        same_mean = sum(same) / len(same)
        nearest_other_mean = min(sum(dists) / len(dists) for dists in other.values())
        silhouette_value = (nearest_other_mean - same_mean) / max(same_mean, nearest_other_mean)
        scores.append(silhouette_value)
    return round(sum(scores) / len(scores), 4)

if __name__ == "__main__":
    score = mean_silhouette_score([(0, 0), (0, 1), (10, 0), (10, 1)], [0, 0, 1, 1])
    assert 0.89 < score < 0.91
