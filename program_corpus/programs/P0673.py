from math import sqrt

def pooled_summary(groups):
    total = sum(n for n, _, _ in groups)
    mean = sum(n * m for n, m, _ in groups) / total
    within = sum((n - 1) * s ** 2 for n, _, s in groups)
    between = sum(n * (m - mean) ** 2 for n, m, _ in groups)
    return round(mean, 3), round(sqrt((within + between) / (total - 1)), 3)

if __name__ == "__main__":
    groups = [(2, 1.0, 0.0), (2, 3.0, 0.0)]
    assert pooled_summary(groups) == (2.0, 1.155)
