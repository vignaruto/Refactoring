"""
Domain: Inventory and Record Management
Task: Find duplicate item records comparing item categories and descriptions.
"""

from typing import List, Dict, Set

def identify_duplicate_records(catalogs: List[List[Dict[str, str]]]) -> Set[str]:
    seen = set()
    duplicates = set()
    for catalog in catalogs:
        for entry in catalog:
            item_key = entry["brand"].strip().lower() + ":" + entry["model"].strip().lower()
            if item_key in seen:
                duplicates.add(item_key)
            else:
                seen.add(item_key)
    return duplicates

if __name__ == "__main__":
    c1 = [{"brand": "Dell", "model": "XPS13"}]
    c2 = [{"brand": "dell ", "model": "xps13"}]
    assert "dell:xps13" in identify_duplicate_records([c1, c2])
