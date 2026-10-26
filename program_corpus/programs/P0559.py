def service_record_errors(record):
    """Return the names of the fields that fail validation."""
    errors = []
    km = record.get("odometer_km", -1)
    if not record.get("vin") or len(record["vin"]) != 17:
        errors.append("vin")
    if km < 0 or km > 2_000_000 or not isinstance(km, int):
        errors.append("odometer")
    if record.get("next_due_km") is not None and record["next_due_km"] <= km:
        errors.append("next_due")
    return errors

if __name__ == "__main__":
    good = {"vin": "1HGCM82633A004352", "odometer_km": 5000}
    assert service_record_errors(good) == []
    bad = {"vin": "X", "odometer_km": -3, "next_due_km": -10}
    assert service_record_errors(bad) == ["vin", "odometer", "next_due"]
