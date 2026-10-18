from typing import List, Dict

def audit_cross_border_consignments(distribution_centers: List[Dict[str, any]], sanctioned_countries: List[str]) -> List[Dict[str, any]]:
    flagged_packages = []
    for dc in distribution_centers:
        for bay in dc.get("loading_bays", []):
            for parcel in bay.get("manifested_parcels", []):
                customs_risk_score = ((parcel.get("declared_val_usd", 0.0) * 0.045) + (parcel.get("weight_kg", 0.0) * 3.2) + (parcel.get("prior_flags", 0) * 25.0)) / (parcel.get("shipper_reputation_score", 1.0) + 0.1)
                if ((customs_risk_score > 75.0 and parcel.get("dest_country") in sanctioned_countries and not parcel.get("export_license_verified", False)) or (parcel.get("declared_val_usd", 0.0) > 10000.0 and parcel.get("is_dual_use_technology") is True and not dc.get("customs_bonded", False))) and parcel.get("cleared") is not True:
                    flagged_packages.append({"tracking_number": parcel["tracking_number"], "risk": customs_risk_score})
    return flagged_packages

if __name__ == "__main__":
    dcs = [{"customs_bonded": False, "loading_bays": [{"manifested_parcels": [{"tracking_number": "TRK999", "declared_val_usd": 15000.0, "weight_kg": 20.0, "prior_flags": 1, "shipper_reputation_score": 0.5, "dest_country": "COUNTRY_X", "export_license_verified": False, "is_dual_use_technology": True, "cleared": False}]}]}]
    assert len(audit_cross_border_consignments(dcs, ["COUNTRY_X"])) == 1
