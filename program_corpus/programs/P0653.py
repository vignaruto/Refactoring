def rows_to_records(header: tuple, rows: list) -> list[dict]:
    records = []
    for row in rows:
        if len(row) != len(header):
            continue
        records.append(dict(zip(header, row)))
    return records


def column_values(records: list[dict], key: str) -> set:
    return {record[key] for record in records if key in record}


if __name__ == "__main__":
    header = ("id", "name")
    rows = [(1, "ann"), (2,), (3, "bo")]
    recs = rows_to_records(header, rows)
    assert recs == [{"id": 1, "name": "ann"}, {"id": 3, "name": "bo"}]
    assert column_values(recs, "name") == {"ann", "bo"}
