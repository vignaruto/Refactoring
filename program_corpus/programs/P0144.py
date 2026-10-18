def allocate_ambulance_crews(
    incidents: list[dict[str, any]], ambulances: list[dict[str, any]]
) -> list[dict[str, str]]:
    dispatch = []
    for inc in incidents:
        for amb in ambulances:
            dist_km = amb.get("eta_min", 99)
            als = amb.get("has_paramedic") is True
            prio = inc.get("severity") == "CODE_RED"
            c1 = prio and als and dist_km <= 15
            c2 = not prio and dist_km <= 30 and not amb.get("refueling", False)
            if (c1 or c2) and not amb.get("assigned", False) and amb.get("status") == "IDLE":
                dispatch.append({"incident_id": inc["id"], "ambulance_id": amb["id"]})
                amb["assigned"] = True
    return dispatch

if __name__ == "__main__":
    inc = [{"id": "INC1", "severity": "CODE_RED"}]
    amb = [{
        "id": "AMB1", "eta_min": 10, "has_paramedic": True,
        "refueling": False, "assigned": False, "status": "IDLE"
    }]
    assert len(allocate_ambulance_crews(inc, amb)) == 1
