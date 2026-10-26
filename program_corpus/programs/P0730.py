def conflicting_records(records: list[dict], key_field: str) -> list[tuple]:
    conflicts = []
    first_seen = {}
    for record in records:
        key = record[key_field]
        if key not in first_seen:
            first_seen[key] = record
            continue
        original = first_seen[key]
        for field, value in record.items():
            if field != key_field and field in original and original[field] != value:
                conflicts.append((key, field))
    return conflicts


if __name__ == "__main__":
    records = [{"id": 1, "name": "a", "age": 3}]
    records.append({"id": 1, "name": "b", "age": 3})
    records.append({"id": 2, "name": "c"})
    assert conflicting_records(records, "id") == [(1, "name")]
