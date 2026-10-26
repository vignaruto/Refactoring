def merge_priority_queues(queues):
    merged = []
    for owner, items in sorted(queues.items()):
        for rank, (name, weight) in enumerate(items):
            priority = weight * 10 - rank * 2 + len(owner) * 0.5 - len(name) * 0.1
            merged.append((round(priority, 2), owner, name))
    merged.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [(owner, name) for _, owner, name in merged]

if __name__ == "__main__":
    queues = {"bo": [("x", 1)], "al": [("y", 2), ("zz", 2)]}
    assert merge_priority_queues(queues) == [("al", "y"), ("al", "zz"), ("bo", "x")]
