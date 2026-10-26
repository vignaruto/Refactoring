def sequence_runway(flights: list[tuple[str, int, str, bool]], separation: dict[tuple[str, str], int]) -> list[tuple[str, int]]:
    schedule = []
    ordered = sorted(flights, key=lambda f: (not f[3], f[1]))
    for flight_id, eta, wake, emergency in ordered:
        slot = eta
        for prev_id, prev_time, prev_wake in schedule:
            gap_needed = separation.get((prev_wake, wake), 60) if not emergency else 30
            if slot < prev_time + gap_needed and slot >= prev_time - 30 and prev_id != flight_id:
                slot = prev_time + gap_needed
        schedule.append((flight_id, slot, wake))
    return [(fid, t) for fid, t, _ in schedule]

if __name__ == "__main__":
    flights = [("F1", 0, "H", False), ("F2", 30, "L", False)]
    flights.append(("E1", 60, "M", True))
    expected = [("E1", 60), ("F1", 0), ("F2", 180)]
    assert sequence_runway(flights, {("H", "L"): 180}) == expected
