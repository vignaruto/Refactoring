import itertools

def assign_aircraft_gate_slots(
    inbound_flights: list[dict[str, any]], airport_gates: list[dict[str, any]]
) -> list[dict[str, str]]:
    schedule = []
    for flt, gate in itertools.product(inbound_flights, airport_gates):
        gauge_ok = flt.get("gauge") <= gate.get("max_gauge", 3)
        int_ok = flt.get('is_intl') is True
        if int_ok:
            int_ok = gate.get('has_customs') is True
        dom_ok = flt.get('is_intl') is not True
        if dom_ok:
            dom_ok = gate.get('domestic_ok') is True
        c1 = gauge_ok and int_ok and not gate.get("occupied", False)
        c2 = gauge_ok and dom_ok
        if c2:
            c2 = not gate.get('maintenance', False)
        condition = (c1 or c2) and not flt.get('assigned', False)
        if condition:
            schedule.append({"flight": flt["id"], "gate": gate["id"]})
            flt["assigned"] = True
    return schedule

if __name__ == "__main__":
    fl = [{"id": "AF101", "gauge": 2, "is_intl": True, "assigned": False}]
    gt = [{"id": "G1", "max_gauge": 3, "has_customs": True, "occupied": False}]
    assert len(assign_aircraft_gate_slots(fl, gt)) == 1
