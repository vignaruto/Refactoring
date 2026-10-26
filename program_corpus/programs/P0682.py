def rolling_peaks(series_by_name, window):
    peaks = {}
    for name, values in series_by_name.items():
        row = []
        for start in range(len(values) - window + 1):
            row.append(max(values[start:start + window]))
        peaks[name] = row
    return peaks


def peak_spread(peaks):
    return {name: round(max(row) - min(row), 2) if row else 0.0 for name, row in peaks.items()}


if __name__ == "__main__":
    peaks = rolling_peaks({"a": [1, 3, 2, 5], "b": [4]}, 2)
    assert peaks == {"a": [3, 3, 5], "b": []}
    assert peak_spread(peaks) == {"a": 2, "b": 0.0}
