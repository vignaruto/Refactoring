"""
Domain: String Processing & Text Analysis
Task: Parse and sanitize multi-attribute key-value tag string.
"""

from typing import Dict

def parse_key_value_tags(tag_string: str) -> Dict[str, str]:
    result = {}
    tokens = tag_string.split(";")
    for token in tokens:
        stripped = token.strip()
        if "=" in stripped:
            key, val = stripped.split("=", 1)
            result[key.strip()] = val.strip()
    return result

if __name__ == "__main__":
    raw = "env=prod; debug=false; region=eu-central"
    parsed = parse_key_value_tags(raw)
    assert parsed["env"] == "prod"
    assert parsed["debug"] == "false"
