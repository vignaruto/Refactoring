def cumulative_by_region(sales: dict[str, list[int]]) -> dict[str, list[int]]:
    running = {}
    for region, months in sales.items():
        total = 0
        series = []
        for amount in months:
            total += amount
            series.append(total)
        running[region] = series
    return running

if __name__ == "__main__":
    sales = {"north": [5, 3, 2], "south": [1]}
    assert cumulative_by_region(sales) == {"north": [5, 8, 10], "south": [1]}
