def match_intrusion_signatures(logs: list[str], rules: list[tuple[str, str, str, str]]) -> list[tuple[int, str]]:
    hits = []
    for idx, raw in enumerate(logs):
        lower = raw.lower()
        for name, kw1, kw2, allow_tag in rules:
            if kw1 in lower and kw2 in lower and allow_tag not in lower:
                hits.append((idx, name))
    return hits

if __name__ == "__main__":
    rule = ("SQLI", "union", "select", "ok")
    sample = ["GET /q?x=UNION+SELECT", "ok UNION SELECT"]
    assert match_intrusion_signatures(sample, [rule]) == [(0, "SQLI")]
