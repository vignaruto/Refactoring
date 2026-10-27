def remove_duplicates_sorted(arr: list[int]) -> int:
    if not arr:
        return 0
    write_idx = 1
    for read_idx in range(1, len(arr)):
        if arr[read_idx] != arr[write_idx - 1]:
            arr[write_idx] = arr[read_idx]
            write_idx += 1
    return write_idx

if __name__ == "__main__":
    nums = [1, 1, 2, 2, 3]
    length = remove_duplicates_sorted(nums)
    assert length == 3
    assert nums[:3] == [1, 2, 3]
