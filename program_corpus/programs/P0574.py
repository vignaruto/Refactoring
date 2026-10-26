def pivot_sales(rows, regions, months):
    table = {r: {m: 0 for m in months} for r in regions}
    for region in regions:
        for region_name, month, amount, refunded in rows:
            if region_name == region and month in table[region] and not refunded:
                table[region][month] += amount
    return table

if __name__ == "__main__":
    rows = [("N", "jan", 5, False), ("N", "jan", 3, True)]
    rows.append(("S", "feb", 4, False))
    table = pivot_sales(rows, ["N", "S"], ["jan", "feb"])
    assert table == {"N": {"jan": 5, "feb": 0}, "S": {"jan": 0, "feb": 4}}
