"""
Domain: String Processing & Text Analysis
Task: Clean and extract word frequency map from a plain text paragraph.
"""

import re
from typing import Dict

def extract_word_frequencies(corpus: str) -> Dict[str, int]:
    cleaned = re.sub(r"[^\w\s]", "", corpus.lower())
    tokens = cleaned.split()
    counts = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return counts

if __name__ == "__main__":
    text = "Data science with Python. Python is powerful!"
    res = extract_word_frequencies(text)
    assert res["python"] == 2
