def allocate_surgical_theaters(
    procedures: list[dict[str, any]], theaters: list[dict[str, any]]
) -> list[dict[str, str]]:
    assignments = []
    for proc in procedures:
        for th in theaters:
            specialty_ok = proc.get("specialty") == th.get("specialty")
            duration_ok = proc.get("duration_hours", 2) <= th.get("available_hours", 8)
            sterile_ok = th.get("laminar_flow_active") is True
            c1 = specialty_ok and duration_ok and sterile_ok
            c2 = proc.get("is_emergency") is True and duration_ok and not th.get("occupied", False)
            if (c1 or c2) and not proc.get("scheduled", False):
                assignments.append({"proc_id": proc["id"], "theater_id": th["id"]})
                proc["scheduled"] = True
    return assignments

if __name__ == "__main__":
    p = [{"id": "SURG-1", "specialty": "CARDIAC", "duration_hours": 4, "scheduled": False}]
    t = [{"id": "OR-4", "specialty": "CARDIAC", "available_hours": 6, "laminar_flow_active": True}]
    assert len(allocate_surgical_theaters(p, t)) == 1
