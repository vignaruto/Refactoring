def can_castle(king_moved: bool, rook_moved: bool, path: list[tuple[str, str]], attacked: set[str], in_check: bool) -> bool:
    path_clear = all(piece == "." for _, piece in path)
    if king_moved or rook_moved or in_check or not path_clear:
        return False
    king_squares = [name for name, _ in path[:2]]
    return not any(name in attacked for name in king_squares)

if __name__ == "__main__":
    path = [("f1", "."), ("g1", ".")]
    assert can_castle(False, False, path, set(), False) is True
    assert can_castle(False, False, path, {"f1"}, False) is False
    assert can_castle(False, False, [("f1", "N")], set(), False) is False
