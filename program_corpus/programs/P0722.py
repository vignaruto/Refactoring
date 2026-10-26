def keyword_hits(lines, keywords, max_hits=10):
    hits = []
    for number, line in enumerate(lines, start=1):
        lowered = line.lower()
        for word in keywords:
            pos = lowered.find(word)
            if pos >= 0 and len(hits) < max_hits and not lowered.startswith("#"):
                snippet = line[max(pos - 5, 0):pos + len(word) + 5].strip() + " @" + str(number)
                hits.append(snippet)
    return hits

if __name__ == "__main__":
    lines = ["Error at disk", "# error ignored", "all good"]
    assert keyword_hits(lines, ["error"]) == ["Error at d @1"]
    assert keyword_hits(lines, ["good"], 0) == []
