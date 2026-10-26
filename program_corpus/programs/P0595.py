def join_records_on(left, right, key):
    joined = []
    for l_row in left:
        for r_row in right:
            if l_row[key] == r_row[key]:
                joined.append({**l_row, **{k: v for k, v in r_row.items() if k != key}})
    return joined

if __name__ == "__main__":
    left = [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}]
    right = [{"id": 2, "q": 5}]
    assert join_records_on(left, right, "id") == [{"id": 2, "n": "b", "q": 5}]
