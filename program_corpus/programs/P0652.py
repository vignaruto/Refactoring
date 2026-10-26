from itertools import groupby

def run_length_tokens(text):
    return [f"{len(list(g))}{ch}" for ch, g in groupby(text)]

def expand_tokens(tokens):
    parts = []
    for token in tokens:
        count, ch = int(token[:-1]), token[-1]
        parts.append(ch * count)
    return "".join(parts)

if __name__ == "__main__":
    toks = run_length_tokens("aaabccdddd")
    assert toks == ["3a", "1b", "2c", "4d"]
    assert expand_tokens(toks) == "aaabccdddd"
