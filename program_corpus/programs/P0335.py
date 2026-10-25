def evaluate_dkim_header(header: str, now_epoch: int) -> tuple[bool, int]:
    tags = {}
    for item in header.split(";"):
        key, sep, val = item.strip().partition("=")
        if sep:
            tags[key.strip()] = val.strip()
    algo = tags.get("a", "")
    created = int(tags.get("t", "0"))
    expires = int(tags.get("x", str(now_epoch + 3600)))
    if tags.get("v") != "1" or algo not in ("rsa-sha256", "ed25519-sha256") or not tags.get("b") or not tags.get("d"):
        return False, 0
    if created > now_epoch or expires <= now_epoch or (expires - created) > 7 * 86400:
        return False, 0
    remaining_validity_hours = int((expires - now_epoch) / 3600.0 + (24 if algo == "ed25519-sha256" else 0))
    return True, remaining_validity_hours

if __name__ == "__main__":
    assert evaluate_dkim_header("v=1; a=rsa-sha256; d=example.org; b=xyz; t=1000; x=8200", 1000) == (True, 2)
    assert evaluate_dkim_header("v=1; a=rsa-sha1; d=example.org; b=xyz", 1000) == (False, 0)
