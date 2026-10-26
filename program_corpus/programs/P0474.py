def can_swap_shifts(worker_a: dict, worker_b: dict, shift_hours: int) -> bool:
    same_role = worker_a["role"] == worker_b["role"]
    a_hours = worker_a["week_hours"]
    b_hours = worker_b["week_hours"]
    if not same_role or a_hours + shift_hours > 48 or b_hours + shift_hours > 48:
        return False
    return worker_a["certified"] and worker_b["certified"]

if __name__ == "__main__":
    a = dict(role="rn", week_hours=40, certified=True)
    b = dict(role="rn", week_hours=36, certified=True)
    assert can_swap_shifts(a, b, 8) is True
    assert can_swap_shifts(a, b, 12) is False
