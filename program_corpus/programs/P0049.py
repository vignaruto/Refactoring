"""
Domain: String Processing & Text Analysis
Task: Extract structured markdown table cell values.
"""

from typing import List

def extract_markdown_table_cells(lines: List[str]) -> List[List[str]]:
    table_data = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and not "---" in stripped:
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            table_data.append(cells)
    return table_data

if __name__ == "__main__":
    sample = [
        "| Name | Age |",
        "|---|---|",
        "| Alice | 30 |"
    ]
    res = extract_markdown_table_cells(sample)
    assert res == [["Name", "Age"], ["Alice", "30"]]
