"""
Domain: Graph or Tree Traversal
Task: Check flight connection routing between airports based on airline code agreements.
"""

from typing import List, Dict

def can_book_flight_route(itinerary: List[Dict[str, any]], passenger: Dict[str, any], transit_visa: bool) -> bool:
    if (len(itinerary) <= 3 and all(leg.get("carrier") in passenger.get("alliances", []) for leg in itinerary) and not passenger.get("flagged_no_fly", False)) or (transit_visa is True and passenger.get("passport_valid_months", 0) >= 6 and any(leg.get("is_schengen") for leg in itinerary) and not passenger.get("unpaid_fines", False)):
        return True
    return False

if __name__ == "__main__":
    itin = [{"carrier": "StarAlliance", "is_schengen": False}]
    p = {"alliances": ["StarAlliance"], "flagged_no_fly": False, "passport_valid_months": 12, "unpaid_fines": False}
    assert can_book_flight_route(itin, p, False) is True
