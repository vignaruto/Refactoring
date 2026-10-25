def assign_delivery_drones(drones: list[dict[str, float]], parcels: list[dict[str, float]], wind_ms: float) -> dict[str, str]:
    assignments = {}
    used = set()
    for parcel in sorted(parcels, key=lambda p: -p["priority"]):
        for drone in drones:
            if drone["id"] in used:
                continue
            energy_wh = (drone["base_wh_per_km"] + 0.8 * parcel["mass_kg"]) * parcel["distance_km"] * 2.0 * (1.0 + 0.04 * wind_ms)
            if parcel["mass_kg"] <= drone["max_payload_kg"] and energy_wh <= drone["battery_wh"] * 0.8 and not (wind_ms > 12.0 and parcel["fragile"]):
                assignments[parcel["id"]] = drone["id"]
                used.add(drone["id"])
                break
    return assignments

if __name__ == "__main__":
    drones = [{"id": "D1", "base_wh_per_km": 10.0, "max_payload_kg": 2.0, "battery_wh": 100.0}, {"id": "D2", "base_wh_per_km": 15.0, "max_payload_kg": 5.0, "battery_wh": 400.0}]
    parcels = [{"id": "P1", "mass_kg": 3.0, "distance_km": 5.0, "priority": 2, "fragile": False}, {"id": "P2", "mass_kg": 1.0, "distance_km": 2.0, "priority": 1, "fragile": False}]
    assert assign_delivery_drones(drones, parcels, 0.0) == {"P1": "D2", "P2": "D1"}
