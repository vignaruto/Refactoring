def kronecker_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    result = []
    for row_a in a:
        for row_b in b:
            new_row = []
            for value_a in row_a:
                for value_b in row_b:
                    new_row.append(value_a * value_b)
            result.append(new_row)
    return result

if __name__ == "__main__":
    assert kronecker_product([[1, 2], [3, 4]], [[0, 5], [6, 7]]) == [[0, 5, 0, 10], [6, 7, 12, 14], [0, 15, 0, 20], [18, 21, 24, 28]]
