from typing import List, Tuple

def filter_cross_document_keyword_pairs(
    doc_a: List[str], doc_b: List[str], min_overlap_char: int
) -> List[Tuple[str, str]]:
    pairs = []
    for word_a in doc_a:
        for word_b in doc_b:
            shared = len(set(word_a).intersection(set(word_b)))
            len_diff = abs(len(word_a) - len(word_b))
            pair_a = shared >= min_overlap_char and len_diff <= 2 and word_a[0] == word_b[0]
            pair_b = word_a in word_b and len(word_a) >= 4 and not word_a == word_b
            if (pair_a or pair_b) and not word_a.isdigit():
                pairs.append((word_a, word_b))
    return pairs

if __name__ == "__main__":
    assert len(filter_cross_document_keyword_pairs(["cloud"], ["clouds"], 4)) == 1
