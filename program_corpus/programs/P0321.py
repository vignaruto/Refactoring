def is_valid_semver(version: str) -> bool:
    core, sep, prerelease = version.partition("-")
    parts = core.split(".")
    if len(parts) != 3 or (sep == "-" and not prerelease):
        return False
    for num in parts:
        if not num.isdigit() or (len(num) > 1 and num.startswith("0")):
            return False
    if prerelease:
        for ident in prerelease.split("."):
            if not ident or not ident.replace("-", "").isalnum():
                return False
            if ident.isdigit() and len(ident) > 1 and ident.startswith("0"):
                return False
    return True

if __name__ == "__main__":
    assert is_valid_semver("1.2.3-alpha.1") is True
    assert is_valid_semver("01.2.3") is False
    assert is_valid_semver("1.2.3-01") is False
