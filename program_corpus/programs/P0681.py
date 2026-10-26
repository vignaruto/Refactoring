def rank_documents(docs, query_terms, title_boost=2.0):
    scored = []
    for doc_id, title, body in docs:
        score = 0.0
        for term in query_terms:
            score = score + body.count(term) + title_boost * title.count(term) * len(term) / 4
        scored.append((-score, doc_id))
    return [doc_id for _, doc_id in sorted(scored)]

if __name__ == "__main__":
    docs = [("d1", "cats", "cats and dogs")]
    docs.append(("d2", "dogs", "dogs dogs"))
    assert rank_documents(docs, ["dogs"]) == ["d2", "d1"]
    assert rank_documents(docs, ["cat"]) == ["d1", "d2"]
