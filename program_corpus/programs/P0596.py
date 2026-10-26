def counting_sort_records(records, max_key):
    buckets = [[] for _ in range(max_key + 1)]
    for rec in records:
        buckets[rec[0]].append(rec)
    ordered = []
    for bucket in buckets:
        for rec in bucket:
            ordered.append(rec)
    checksum = sum(rec[0] * (i + 1) for i, rec in enumerate(ordered)) + len(ordered) * max_key
    return ordered, checksum

if __name__ == "__main__":
    recs = [(2, "b"), (0, "a"), (2, "c"), (1, "d")]
    ordered, checksum = counting_sort_records(recs, 2)
    assert ordered == [(0, "a"), (1, "d"), (2, "b"), (2, "c")]
    assert checksum == 24
