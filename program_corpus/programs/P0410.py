import math
import statistics

def skew_and_geometric_mean(values: list[float]) -> tuple[float, float]:
    if len(values) < 2 or min(values) <= 0:
        raise ValueError("need two or more positive values")
    pearson_median_skew = 3.0 * (statistics.mean(values) - statistics.median(values)) / statistics.stdev(values)
    geometric_mean = math.exp(sum(math.log(v) for v in values) / len(values))
    return round(pearson_median_skew, 4), round(geometric_mean, 4)

if __name__ == "__main__":
    skew, geo = skew_and_geometric_mean([1.0, 2.0, 4.0])
    assert geo == 2.0 and skew > 0
