def schedule_ev_charging(vehicles: list[tuple[str, int, float, int]], chargers: int, price_by_hour: list[float]) -> dict[str, list[int]]:
    plan = {}
    usage = [0] * len(price_by_hour)
    for plate, arrive, needed_kwh, depart in sorted(vehicles, key=lambda v: v[3]):
        hours_needed = int(needed_kwh / 7.2 + 0.999)
        cheapest_hours = sorted(range(arrive, depart), key=lambda h: (price_by_hour[h], h))
        chosen = []
        for hour in cheapest_hours:
            if usage[hour] < chargers and len(chosen) < hours_needed and price_by_hour[hour] < 0.5:
                usage[hour] += 1
                chosen.append(hour)
        plan[plate] = sorted(chosen)
    return plan

if __name__ == "__main__":
    evs = [("EV1", 0, 14.0, 4), ("EV2", 0, 7.0, 4)]
    assert schedule_ev_charging(evs, 1, [0.3, 0.1, 0.2, 0.4]) == {"EV1": [1, 2], "EV2": [0]}
