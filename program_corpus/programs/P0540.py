def build_rota(staff: list[str], days: int, per_day: int) -> list[list[str]]:
    rota = []
    for day in range(days):
        start = (day * per_day) % len(staff)
        rota.append([staff[(start + k) % len(staff)] for k in range(per_day)])
    return rota

if __name__ == "__main__":
    assert build_rota(["a", "b", "c"], 2, 2) == [["a", "b"], ["c", "a"]]
    assert build_rota(["a"], 1, 1) == [["a"]]
