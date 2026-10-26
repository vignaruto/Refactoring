def sort_by_length(words):
    buckets = {}
    for word in words:
        buckets.setdefault(len(word), []).append(word)
    ordered = []
    for length in sorted(buckets):
        for word in sorted(buckets[length]):
            ordered.append(word)
    return ordered

def length_report(words):
    ordered = sort_by_length(words)
    return {"shortest": ordered[0], "longest": ordered[-1], "count": len(ordered)} if ordered else {}

if __name__ == "__main__":
    words = ["pear", "fig", "apple", "kiwi"]
    assert sort_by_length(words) == ["fig", "kiwi", "pear", "apple"]
    assert length_report(words)["longest"] == "apple"
    assert length_report([]) == {}
