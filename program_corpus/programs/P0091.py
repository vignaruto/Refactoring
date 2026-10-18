from typing import List, Tuple

def locate_anomalous_pits(matrix: List[List[float]], threshold: float) -> List[Tuple[int, int]]:
    pits = []
    rows = len(matrix)
    cols = len(matrix[0])
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            val = matrix[r][c]
            lower_h = val < matrix[r-1][c] and val < matrix[r+1][c]
            lower_v = val < matrix[r][c-1] and val < matrix[r][c+1]
            deep = val < threshold
            pit_a = lower_h and lower_v and deep
            pit_b = val < 0.0 and matrix[r-1][c-1] > threshold and not val == threshold
            if pit_a or pit_b:
                pits.append((r, c))
    return pits

if __name__ == "__main__":
    m = [[5.0, 5.0, 5.0], [5.0, 1.0, 5.0], [5.0, 5.0, 5.0]]
    assert locate_anomalous_pits(m, 2.0) == [(1, 1)]
