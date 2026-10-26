def assign_pick_slots(skus: list[tuple[str, int, float]], slots: list[tuple[str, int, float]]) -> dict[str, str]:
    taken = set()
    assignment = {}
    for sku, picks_per_day, unit_weight in sorted(skus, key=lambda s: -s[1]):
        for slot_id, distance_m, max_weight in sorted(slots, key=lambda s: s[1]):
            travel_cost_per_day = 2.0 * distance_m * picks_per_day / 1000.0 * (1.2 if unit_weight > 15 else 1.0)
            if slot_id not in taken and unit_weight <= max_weight and travel_cost_per_day < 50.0:
                assignment[sku] = slot_id
                taken.add(slot_id)
                break
    return assignment

if __name__ == "__main__":
    skus = [("A", 100, 2.0), ("B", 500, 20.0)]
    slots = [("S1", 5, 10.0), ("S2", 10, 25.0)]
    assert assign_pick_slots(skus, slots) == {"B": "S2", "A": "S1"}
