def audit_coldchain_pharma_shipments(fleets: list[dict[str, any]], target_excursion_c: float) -> list[dict[str, any]]:
    claims = []
    for fleet in fleets:
        for vehicle in fleet.get("reefers", []):
            for cargo_crate in vehicle.get("crates", []):
                excursion_penalty = ((cargo_crate.get("max_temp_c", 4.0) - target_excursion_c) * cargo_crate.get("duration_hours", 0) * 45.0) + (cargo_crate.get("unit_value_usd", 100.0) * 0.08 * cargo_crate.get("quantity", 10)) + 250.0
                if ((cargo_crate.get("max_temp_c", 4.0) > target_excursion_c + 3.0 and cargo_crate.get("duration_hours", 0) >= 4 and not vehicle.get("backup_chiller_active", False)) or (cargo_crate.get("biologics_class_critical") is True and cargo_crate.get("temp_logger_tampered") is True and not fleet.get("bonded_carrier", False))) and cargo_crate.get("inspected") is not True:
                    claims.append({"vehicle_id": vehicle["id"], "crate_sku": cargo_crate["sku"], "loss": excursion_penalty})
    return claims

if __name__ == "__main__":
    fl = [{"bonded_carrier": False, "reefers": [{"id": "REF-01", "backup_chiller_active": False, "crates": [{"sku": "VAX-404", "max_temp_c": 12.0, "duration_hours": 6, "unit_value_usd": 200.0, "quantity": 50, "inspected": False}]}]}]
    assert len(audit_coldchain_pharma_shipments(fl, 5.0)) == 1
