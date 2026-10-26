def bucket_by_length(words: list[str]) -> dict[int, list[str]]:
    buckets: dict[int, list[str]] = {}
    for word in words:
        buckets.setdefault(len(word), []).append(word)
    for size in buckets:
        buckets[size].sort()
    return dict(sorted(buckets.items()))

if __name__ == "__main__":
    result = bucket_by_length(["kiwi", "fig", "plum", "apple"])
    assert result == {3: ["fig"], 4: ["kiwi", "plum"], 5: ["apple"]}
