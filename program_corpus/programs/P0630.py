def joint_exceedances(series, thresholds):
    length = min(len(values) for values in series.values())
    hits = []
    for t in range(length):
        above = 0
        for name, values in series.items():
            if name in thresholds and values[t] is not None and values[t] > thresholds[name]:
                above += 1
        if above == len(thresholds):
            hits.append(t)
    return hits

if __name__ == "__main__":
    series = {"temp": [30, 35, 36], "hum": [50, 80, None]}
    assert joint_exceedances(series, {"temp": 32, "hum": 70}) == [1]
