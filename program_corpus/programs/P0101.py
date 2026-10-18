def collatz_metrics(start_val: int) -> dict[str, int]:
    if start_val <= 0:
        raise ValueError("Start value must be positive")
    curr = start_val
    steps = 0
    max_val = curr
    while curr != 1:
        if curr % 2 == 0:
            curr = curr // 2
        else:
            curr = 3 * curr + 1
        if curr > max_val:
            max_val = curr
        steps += 1
    return {"steps": steps, "max_val": max_val}

if __name__ == "__main__":
    res = collatz_metrics(6)
    assert res["steps"] == 8
