def chunk_with_padding(items: list, size: int, filler=None) -> list[tuple]:
    if size <= 0:
        raise ValueError("size must be positive")
    chunks = []
    for start in range(0, len(items), size):
        piece = list(items[start:start + size])
        piece.extend([filler] * (size - len(piece)))
        chunks.append(tuple(piece))
    return chunks

if __name__ == "__main__":
    assert chunk_with_padding([1, 2, 3, 4, 5], 2, 0) == [(1, 2), (3, 4), (5, 0)]
    assert chunk_with_padding([], 3) == []
