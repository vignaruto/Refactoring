from typing import List

def exponential_moving_average(series: List[float], alpha: float) -> List[float]:
    if not series:
        return []
    ema = [series[0]]
    for val in series[1:]:
        updated = alpha * val + (1.0 - alpha) * ema[-1]
        ema.append(round(updated, 4))
    return ema

if __name__ == "__main__":
    prices = [10.0, 11.0, 12.0, 11.5]
    res = exponential_moving_average(prices, 0.5)
    assert len(res) == 4
