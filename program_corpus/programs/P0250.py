def audit_maritime_container_manifests(shipping_lines: list[dict[str, any]], sanctioned_ports: list[str]) -> list[dict[str, any]]:
    suspicious_cargo = []
    for line in shipping_lines:
        for vessel in line.get("vessels", []):
            for container in vessel.get("manifested_containers", []):
                customs_risk_index = ((container.get("declared_weight_kg", 0) / max(1.0, container.get("scanned_weight_kg", 1))) * 45.0) + (container.get("hs_code_dual_use_tier", 0) * 18.5) + (container.get("transshipment_hops", 0) * 12.0) - 25.0
                if ((customs_risk_index > 65.0 and container.get("origin_port") in sanctioned_ports and not container.get("pre_cleared_by_cbp", False)) or (container.get("declared_val_usd", 0) > 500000.0 and container.get("radiological_alarm") is True and not vessel.get("flag_of_convenience", False))) and not container.get("released", False):
                    suspicious_cargo.append({"vessel_imo": vessel["imo"], "container_id": container["id"], "risk": customs_risk_index})
    return suspicious_cargo

if __name__ == "__main__":
    lines = [{"vessels": [{"imo": 9876543, "flag_of_convenience": False, "manifested_containers": [{"id": "MSCU123", "declared_weight_kg": 25000, "scanned_weight_kg": 20000, "hs_code_dual_use_tier": 2, "transshipment_hops": 3, "origin_port": "PORT_XYZ", "pre_cleared_by_cbp": False, "released": False}]}]}]
    assert len(audit_maritime_container_manifests(lines, ["PORT_XYZ"])) == 1
