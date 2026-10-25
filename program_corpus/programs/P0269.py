def chi_square_statistic(table: list[list[int]]) -> float:
    row_totals = [sum(row) for row in table]
    col_totals = [sum(col) for col in zip(*table)]
    grand_total = sum(row_totals)
    statistic = 0.0
    for i, row in enumerate(table):
        for j, observed in enumerate(row):
            expected = row_totals[i] * col_totals[j] / grand_total
            statistic += (observed - expected) ** 2 / expected
    return round(statistic, 4)

if __name__ == "__main__":
    assert chi_square_statistic([[10, 20], [20, 10]]) == 6.6667
    assert chi_square_statistic([[5, 5], [5, 5]]) == 0.0
