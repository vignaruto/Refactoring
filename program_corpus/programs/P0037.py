"""
Domain: Lists, Tuples, Dictionaries, and Sets
Task: Verify employee access eligibility against security tiers and geo-fencing.
"""

from typing import Dict

def is_secure_door_access_granted(employee: Dict[str, any], terminal: Dict[str, any], access_time_hour: int) -> bool:
    is_granted = bool((employee.get("clearance") >= terminal.get("min_clearance", 5) and (terminal.get("building_id") in employee.get("authorized_buildings", [])) and (8 <= access_time_hour <= 18 or employee.get("night_access") is True)) or (employee.get("is_emergency_first_responder") is True and terminal.get("lockdown_override") is True and not employee.get("revoked", False)))
    return is_granted

if __name__ == "__main__":
    emp = {"clearance": 7, "authorized_buildings": ["B1", "B2"], "night_access": False, "is_emergency_first_responder": False, "revoked": False}
    term = {"min_clearance": 5, "building_id": "B1", "lockdown_override": False}
    assert is_secure_door_access_granted(emp, term, 14) is True
