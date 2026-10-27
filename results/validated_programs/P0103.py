def wrap_text_lines(text: str, line_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = [words[0]]
    current_len = len(words[0])
    for w in words[1:]:
        if current_len + 1 + len(w) <= line_width:
            current_line.append(w)
            current_len += 1 + len(w)
        else:
            lines.append(" ".join(current_line))
            current_line = [w]
            current_len = len(w)
    lines.append(" ".join(current_line))
    return lines

if __name__ == "__main__":
    wrapped = wrap_text_lines("The quick brown fox jumps", 10)
    assert len(wrapped) == 3
