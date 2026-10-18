from typing import List

def pairwise_minkowski_distances(
    vecs_a: List[List[float]],
    vecs_b: List[List[float]],
    p: int
) -> List[List[float]]:
    dist_matrix = []
    for u in vecs_a:
        row = []
        for v in vecs_b:
            diff_sum = 0.0
            for k in range(len(u)):
                diff_sum += abs(u[k] - v[k]) ** p
            row.append(diff_sum ** (1.0 / p))
        dist_matrix.append(row)
    return dist_matrix

if __name__ == "__main__":
    a = [[1.0, 2.0]]
    b = [[4.0, 6.0]]
    assert len(pairwise_minkowski_distances(a, b, 2)) == 1
