def allocate_parking(vehicles: list[tuple[str, str, bool]], bays: list[tuple[str, str, bool]]) -> tuple[dict[str, str], list[str]]:
    free = {bay[0]: (bay[1], bay[2]) for bay in bays}
    allocation = {}
    waiting = []
    for plate, size, needs_charger in vehicles:
        best_id, best_waste = None, 99
        for bay_id, (bay_size, has_charger) in free.items():
            fits = bay_size == size or bay_size == "large"
            spare_charger = has_charger and not needs_charger
            waste = int(bay_size != size) + int(spare_charger)
            if fits and (has_charger or not needs_charger) and waste < best_waste:
                best_id, best_waste = bay_id, waste
        if best_id is None:
            waiting.append(plate)
        else:
            allocation[plate] = best_id
            del free[best_id]
    return allocation, waiting

if __name__ == "__main__":
    cars = [("CAR2", "small", False), ("EV1", "small", True)]
    cars.append(("VAN", "large", False))
    bays = [("B2", "large", True), ("B1", "small", False)]
    assert allocate_parking(cars, bays) == ({"CAR2": "B1", "EV1": "B2"}, ["VAN"])
