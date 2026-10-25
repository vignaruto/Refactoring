import math

def bm25_term_score(term_freq: int, doc_len: int, avg_doc_len: float, total_docs: int, docs_with_term: int) -> float:
    k1 = 1.5
    b = 0.75
    idf = math.log(1.0 + (total_docs - docs_with_term + 0.5) / (docs_with_term + 0.5))
    tf_norm = (term_freq * (k1 + 1.0)) / (term_freq + k1 * (1.0 - b + b * (doc_len / avg_doc_len)))
    return round(idf * tf_norm, 4)

if __name__ == "__main__":
    assert bm25_term_score(3, 120, 100.0, 1000, 50) > 4.0
    assert bm25_term_score(0, 120, 100.0, 1000, 50) == 0.0
