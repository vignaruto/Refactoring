def chunk_padded(items, size, fill=None):
    chunks = []
    for start in range(0, len(items), size):
        chunk = list(items[start:start + size])
        chunk.extend([fill] * (size - len(chunk)))
        chunks.append(tuple(chunk))
    return chunks

def unchunk(chunks, fill=None):
    flat = [x for chunk in chunks for x in chunk]
    while flat and flat[-1] == fill:
        flat.pop()
    return flat

if __name__ == "__main__":
    chunks = chunk_padded([1, 2, 3, 4, 5], 2)
    assert chunks == [(1, 2), (3, 4), (5, None)]
    assert unchunk(chunks) == [1, 2, 3, 4, 5]
