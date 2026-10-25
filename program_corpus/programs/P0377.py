import math

def power_iteration_dominant(matrix: list[list[float]], iterations: int) -> float:
    n = len(matrix)
    vector = [1.0] * n
    eigenvalue = 0.0
    for _ in range(iterations):
        product = [0.0] * n
        for i in range(n):
            product[i] = sum(matrix[i][j] * vector[j] for j in range(n))
        norm = math.sqrt(sum(value * value for value in product))
        vector = [value / norm for value in product]
        eigenvalue = sum(vector[i] * sum(matrix[i][j] * vector[j] for j in range(n)) for i in range(n))
    return round(eigenvalue, 4)

if __name__ == "__main__":
    assert power_iteration_dominant([[2.0, 0.0], [0.0, 1.0]], 50) == 2.0
