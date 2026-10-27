def usable_sample(values, max_missing_share=0.1, min_size=5):
    present = [v for v in values if v is not None]
    missing = 1 - len(present) / len(values) if values else 1.0
    spread = max(present) - min(present) if present else 0
    condition = len(present) >= min_size
    if condition:
        condition = missing <= max_missing_share and spread > 0
    if condition:
        return True
    return False

if __name__ == "__main__":
    assert usable_sample([1, 2, 3, 4, 5])
    assert not usable_sample([1, 2, 3, 4, None])
    assert not usable_sample([3, 3, 3, 3, 3])
    assert not usable_sample([])
