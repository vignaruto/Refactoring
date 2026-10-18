from typing import List, Set

def find_common_word_ngrams(words_a: List[str], words_b: List[str]) -> Set[str]:
    common = set()
    for word_1 in words_a:
        for word_2 in words_b:
            len_min = min(len(word_1), len(word_2))
            for k in range(3, len_min + 1):
                sub = word_1[:k]
                if sub in word_2:
                    common.add(sub)
    return common

if __name__ == "__main__":
    res = find_common_word_ngrams(["transformation", "reform"], ["transfer", "formation"])
    assert "trans" in res or "form" in res
