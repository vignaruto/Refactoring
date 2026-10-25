def rotate_right_by(items: list[int], k: int) -> list[int]:
    if not items:
        return []
    shift = k % len(items)
    if shift == 0:
        return list(items)
    return items[-shift:] + items[:-shift]

if __name__ == "__main__":
    assert rotate_right_by([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert rotate_right_by([1, 2, 3], 3) == [1, 2, 3]
    assert rotate_right_by([], 4) == []
