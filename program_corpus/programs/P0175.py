def is_agri_export_exempt(
    cargo: dict[str, any], destination: str, fta_signatory: bool
) -> bool:
    organic = cargo.get("is_certified_organic") is True
    origin_ok = cargo.get("origin_country") in ("US", "CA", "MX")
    val_low = cargo.get("invoice_val_usd", 0.0) <= 25000.0
    sanitary_cert = cargo.get("phytosanitary_passed") is True
    cond_org = organic and origin_ok and sanitary_cert
    cond_fta = fta_signatory and val_low
    if (cond_org or cond_fta) and not cargo.get("quarantined", False):
        return True
    return False

if __name__ == "__main__":
    c = {
        "is_certified_organic": True, "origin_country": "US",
        "phytosanitary_passed": True, "quarantined": False
    }
    assert is_agri_export_exempt(c, "CA", True) is True
