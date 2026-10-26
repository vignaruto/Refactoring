def window_maxima(series: list[float], width: int) -> list[float]:
    result = []
    for start in range(len(series) - width + 1):
        top = series[start]
        for offset in range(1, width):
            top = max(top, series[start + offset])
        result.append(top)
    return result

if __name__ == "__main__":
    assert window_maxima([1, 3, 2, 5, 4], 2) == [3, 3, 5, 5]
    assert window_maxima([1, 3, 2], 3) == [3]
