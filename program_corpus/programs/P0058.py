from typing import Tuple

def consume_token(
    capacity: float, current_tokens: float,
    refill_rate: float, elapsed_sec: float
) -> Tuple[bool, float]:
    refilled = current_tokens + (elapsed_sec * refill_rate)
    pool = min(capacity, refilled)
    if pool >= 1.0:
        return True, pool - 1.0
    return False, pool

if __name__ == "__main__":
    allowed, tokens = consume_token(10.0, 0.5, 2.0, 1.0)
    assert allowed is True
    assert tokens == 1.5
