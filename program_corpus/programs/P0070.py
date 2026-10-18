from typing import List, Dict, Tuple

def generate_item_pair_frequencies(baskets: List[List[str]]) -> Dict[Tuple[str, str], int]:
    pair_counts = {}
    for basket in baskets:
        sorted_items = sorted(basket)
        for i in range(len(sorted_items)):
            for j in range(i + 1, len(sorted_items)):
                pair = (sorted_items[i], sorted_items[j])
                current = pair_counts.get(pair, 0)
                pair_counts[pair] = current + 1
    return pair_counts

if __name__ == "__main__":
    sample = [["milk", "bread", "eggs"], ["milk", "bread"]]
    counts = generate_item_pair_frequencies(sample)
    assert counts[("bread", "milk")] == 2
