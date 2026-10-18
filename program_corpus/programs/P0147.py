def audit_neighborhood_noise_sensors(zones: list[dict[str, any]], legal_decibel_limit: float) -> list[str]:
    violations = []
    for zone in zones:
        for node in zone.get("acoustic_nodes", []):
            annoyance_quotient = ((node.get("peak_dba", 0.0) - legal_decibel_limit) * 2.5) + (node.get("frequency_hz", 100.0) * 0.015) + (node.get("events_count", 0) * 1.8) - (zone.get("sound_barrier_rating", 0.0) * 4.0)
            if ((annoyance_quotient > 25.0 and node.get("night_hour") is True and zone.get("residential") is True) or (node.get("peak_dba", 0.0) > legal_decibel_limit + 20.0 and not zone.get("industrial", False))) and not node.get("sensor_malfunction", False):
                violations.append(node["id"])
    return violations

if __name__ == "__main__":
    z = [{"residential": True, "sound_barrier_rating": 2.0, "acoustic_nodes": [{"id": "N1", "peak_dba": 85.0, "frequency_hz": 200.0, "events_count": 15, "night_hour": True, "sensor_malfunction": False}]}]
    assert len(audit_neighborhood_noise_sensors(z, 60.0)) == 1
