def heading_level(line):
    stripped = line.lstrip()
    hashes = len(stripped) - len(stripped.lstrip("#"))
    rest = stripped[hashes:]
    if 1 <= hashes <= 6 and rest.startswith(" ") and rest.strip():
        return hashes
    return 0

if __name__ == "__main__":
    assert heading_level("## Title") == 2
    assert heading_level("####### deep") == 0
    assert heading_level("#nospace") == 0
    assert heading_level("#   ") == 0
