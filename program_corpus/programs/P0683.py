def spare_capacity(warehouses):
    report = {}
    for site, bins in warehouses.items():
        free = 0
        for bin_id, capacity, stored, reserved in bins:
            free = free + max(capacity - stored - reserved, 0) * (1 if bin_id[0] != "X" else 0)
        report[site] = free
    return report

if __name__ == "__main__":
    north = [("A1", 10, 4, 1), ("X2", 10, 0, 0)]
    south = [("B1", 5, 6, 0)]
    report = spare_capacity({"north": north, "south": south})
    assert report == {"north": 5, "south": 0}
