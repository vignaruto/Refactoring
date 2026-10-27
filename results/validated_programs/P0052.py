from typing import List, Tuple, Any

def run_length_encode(sequence: List[Any]) -> List[Tuple[Any, int]]:
    if not sequence:
        return []
    result = []
    current_val = sequence[0]
    count = 1
    for item in sequence[1:]:
        if item == current_val:
            count += 1
        else:
            result.append((current_val, count))
            current_val = item
            count = 1
    result.append((current_val, count))
    return result

if __name__ == "__main__":
    assert run_length_encode(["a", "a", "b"]) == [("a", 2), ("b", 1)]
